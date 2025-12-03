from flask import Flask, render_template_string, request, send_file, redirect, url_for, make_response
from PIL import Image
import os
import math
import io
import uuid
import base64
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Use tempfile for temporary storage (works on all platforms)
temp_dir = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = os.path.join(temp_dir, 'image_compressor_temp')

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# HTML Template with CSS (same as before, just changing download endpoint)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Compressor - 200KB to 15KB</title>
    <style>
        /* CSS remains exactly the same as before */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 800px;
            overflow: hidden;
            animation: slideUp 0.5s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        
        .header h1 i {
            font-size: 2.8rem;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
            transition: all 0.3s;
            background: #f8f9ff;
            cursor: pointer;
        }
        
        .upload-area:hover {
            border-color: #764ba2;
            background: #f0f2ff;
            transform: translateY(-2px);
        }
        
        .upload-area.dragover {
            border-color: #4CAF50;
            background: #e8f5e9;
        }
        
        .upload-icon {
            font-size: 4rem;
            color: #667eea;
            margin-bottom: 20px;
        }
        
        .upload-text h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.5rem;
        }
        
        .upload-text p {
            color: #666;
            margin-bottom: 20px;
        }
        
        .browse-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-block;
            margin-top: 10px;
        }
        
        .browse-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .file-input {
            display: none;
        }
        
        .size-controls {
            background: #f8f9ff;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }
        
        .size-controls h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .target-size {
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .size-input {
            flex: 1;
            min-width: 200px;
        }
        
        .size-input label {
            display: block;
            color: #666;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        .size-input input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .size-input input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .size-display {
            background: white;
            padding: 15px;
            border-radius: 10px;
            border: 2px solid #667eea;
            text-align: center;
            min-width: 150px;
        }
        
        .size-display .target {
            font-size: 1.8rem;
            font-weight: bold;
            color: #667eea;
            line-height: 1;
        }
        
        .size-display .label {
            font-size: 0.9rem;
            color: #666;
            margin-top: 5px;
        }
        
        .compress-btn {
            background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
            color: white;
            border: none;
            width: 100%;
            padding: 18px;
            border-radius: 15px;
            font-size: 1.2rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
        }
        
        .compress-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(76, 175, 80, 0.3);
        }
        
        .compress-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .result-area {
            background: #f8f9ff;
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
            display: none;
            animation: fadeIn 0.5s ease-out;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .result-area.show {
            display: block;
        }
        
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .result-header h3 {
            color: #333;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .result-header .success-badge {
            background: #4CAF50;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .image-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 25px;
        }
        
        @media (max-width: 768px) {
            .image-comparison {
                grid-template-columns: 1fr;
            }
        }
        
        .image-box {
            background: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .image-box h4 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.1rem;
            text-align: center;
        }
        
        .image-preview {
            width: 100%;
            height: 200px;
            overflow: hidden;
            border-radius: 8px;
            margin-bottom: 15px;
            background: #f5f5f5;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .image-preview img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        
        .image-stats {
            display: flex;
            justify-content: space-between;
            color: #666;
            font-size: 0.9rem;
        }
        
        .download-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin: 0 auto;
            text-decoration: none;
        }
        
        .download-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .progress-bar {
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            overflow: hidden;
            margin: 20px 0;
            display: none;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }
        
        .footer a {
            color: white;
            text-decoration: none;
            font-weight: 600;
        }
        
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
            animation: shake 0.5s;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        .error-message.show {
            display: block;
        }
        
        .icon {
            display: inline-block;
            font-size: 1.2em;
            vertical-align: middle;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>
                <span class="icon">🖼️</span>
                Image Size Compressor
            </h1>
            <p>Convert 200KB images to 15KB while maintaining quality</p>
        </div>
        
        <div class="content">
            <form id="uploadForm" method="POST" enctype="multipart/form-data">
                <div class="upload-area" id="dropArea">
                    <div class="upload-icon">
                        📤
                    </div>
                    <div class="upload-text">
                        <h3>Upload Your Image</h3>
                        <p>Drag & drop your image here or click to browse</p>
                        <p>Supports JPG, PNG, JPEG, BMP (Max 5MB)</p>
                        <button type="button" class="browse-btn" onclick="document.getElementById('fileInput').click()">
                            Browse Files
                        </button>
                        <input type="file" id="fileInput" class="file-input" name="image" accept=".jpg,.jpeg,.png,.bmp" required>
                    </div>
                </div>
                
                <div class="size-controls">
                    <h3>
                        <span class="icon">🎯</span>
                        Compression Settings
                    </h3>
                    <div class="target-size">
                        <div class="size-input">
                            <label for="targetSize">Target Size (KB)</label>
                            <input type="number" id="targetSize" name="target_size" min="5" max="200" value="15" step="1">
                        </div>
                        <div class="size-display">
                            <div class="target">15 KB</div>
                            <div class="label">Target Size</div>
                        </div>
                    </div>
                </div>
                
                <div class="progress-bar" id="progressBar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                
                <button type="submit" class="compress-btn" id="compressBtn">
                    <span class="icon">⚡</span>
                    Compress Image
                </button>
            </form>
            
            <div class="error-message" id="errorMessage"></div>
            
            <div class="result-area" id="resultArea">
                <div class="result-header">
                    <h3>
                        <span class="icon">✅</span>
                        Compression Successful
                    </h3>
                    <span class="success-badge">COMPRESSED</span>
                </div>
                
                <div class="image-comparison" id="imageComparison">
                    <!-- Images will be loaded here by JavaScript -->
                </div>
                
                <button class="download-btn" id="downloadBtn" onclick="downloadImage()">
                    <span class="icon">⬇️</span>
                    Download Compressed Image
                </button>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Made with ❤️ using Flask & Pillow | Convert 200KB images to 15KB effortlessly</p>
    </div>
    
    <script>
        // Global variable to store compressed data
        let currentCompressedData = null;
        let currentFilename = null;
        
        // DOM Elements
        const fileInput = document.getElementById('fileInput');
        const dropArea = document.getElementById('dropArea');
        const targetSizeInput = document.getElementById('targetSize');
        const sizeDisplay = document.querySelector('.size-display .target');
        const compressBtn = document.getElementById('compressBtn');
        const progressBar = document.getElementById('progressBar');
        const progressFill = document.getElementById('progressFill');
        const resultArea = document.getElementById('resultArea');
        const errorMessage = document.getElementById('errorMessage');
        const imageComparison = document.getElementById('imageComparison');
        const downloadBtn = document.getElementById('downloadBtn');
        
        // Update size display
        targetSizeInput.addEventListener('input', function() {
            sizeDisplay.textContent = this.value + ' KB';
        });
        
        // Drag and drop functionality
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropArea.classList.add('dragover');
        }
        
        function unhighlight() {
            dropArea.classList.remove('dragover');
        }
        
        dropArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            fileInput.files = files;
            updateFileName(files[0]);
        }
        
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                updateFileName(this.files[0]);
            }
        });
        
        function updateFileName(file) {
            const uploadText = dropArea.querySelector('.upload-text h3');
            uploadText.innerHTML = `<span class="icon">📁</span> ${file.name}`;
            dropArea.querySelector('.upload-text p').textContent = 
                `Size: ${(file.size / 1024).toFixed(1)} KB | Type: ${file.type}`;
        }
        
        // Form submission
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const file = fileInput.files[0];
            const targetSize = targetSizeInput.value;
            
            if (!file) {
                showError('Please select an image file first!');
                return;
            }
            
            if (file.size > 5 * 1024 * 1024) {
                showError('File size must be less than 5MB!');
                return;
            }
            
            // Show progress
            compressBtn.disabled = true;
            compressBtn.innerHTML = '<span class="icon">⏳</span> Compressing...';
            progressBar.style.display = 'block';
            progressFill.style.width = '30%';
            
            const formData = new FormData();
            formData.append('image', file);
            formData.append('target_size', targetSize);
            
            try {
                progressFill.style.width = '60%';
                
                const response = await fetch('/compress', {
                    method: 'POST',
                    body: formData
                });
                
                progressFill.style.width = '90%';
                
                const data = await response.json();
                
                if (data.success) {
                    progressFill.style.width = '100%';
                    
                    // Store compressed data for download
                    currentCompressedData = data.compressed_data;
                    currentFilename = data.filename;
                    
                    // Update result area
                    imageComparison.innerHTML = `
                        <div class="image-box">
                            <h4>Original Image</h4>
                            <div class="image-preview">
                                <img src="${data.original_preview}" alt="Original">
                            </div>
                            <div class="image-stats">
                                <span>Size: ${data.original_size_kb} KB</span>
                                <span>${data.original_dimensions}</span>
                            </div>
                        </div>
                        <div class="image-box">
                            <h4>Compressed Image</h4>
                            <div class="image-preview">
                                <img src="${data.compressed_preview}" alt="Compressed">
                            </div>
                            <div class="image-stats">
                                <span>Size: ${data.compressed_size_kb} KB</span>
                                <span>${data.compressed_dimensions}</span>
                            </div>
                        </div>
                    `;
                    
                    // Show result
                    setTimeout(() => {
                        resultArea.classList.add('show');
                        window.scrollTo({
                            top: resultArea.offsetTop - 50,
                            behavior: 'smooth'
                        });
                        progressFill.style.width = '0%';
                        progressBar.style.display = 'none';
                    }, 500);
                    
                } else {
                    showError(data.error || 'Compression failed!');
                }
                
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                compressBtn.disabled = false;
                compressBtn.innerHTML = '<span class="icon">⚡</span> Compress Image';
            }
        });
        
        function downloadImage() {
            if (!currentCompressedData) {
                showError('No compressed image available. Please compress an image first.');
                return;
            }
            
            try {
                // Create download link from base64 data
                const link = document.createElement('a');
                link.href = currentCompressedData;
                link.download = currentFilename || 'compressed_image.jpg';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Show success message
                const originalError = errorMessage.textContent;
                errorMessage.textContent = '✅ Image downloaded successfully!';
                errorMessage.style.background = '#e8f5e9';
                errorMessage.style.color = '#2E7D32';
                errorMessage.classList.add('show');
                
                setTimeout(() => {
                    errorMessage.classList.remove('show');
                    errorMessage.style.background = '';
                    errorMessage.style.color = '';
                    if (originalError) {
                        errorMessage.textContent = originalError;
                    }
                }, 3000);
                
            } catch (error) {
                showError('Download failed: ' + error.message);
            }
        }
        
        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.style.background = '#ffebee';
            errorMessage.style.color = '#c62828';
            errorMessage.classList.add('show');
            compressBtn.disabled = false;
            compressBtn.innerHTML = '<span class="icon">⚡</span> Compress Image';
            progressBar.style.display = 'none';
            
            setTimeout(() => {
                errorMessage.classList.remove('show');
            }, 5000);
        }
    </script>
</body>
</html>
'''

def smart_compress_to_target(img, target_kb=15):
    """
    Smart tarike se image compress karna specific target size tak
    """
    # Original dimensions
    orig_width, orig_height = img.size
    
    # Format check
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    
    # Target size in bytes
    target_bytes = target_kb * 1024
    
    # Step 1: Start with reasonable dimensions
    max_dimension = 1200
    if max(orig_width, orig_height) > max_dimension:
        ratio = max_dimension / max(orig_width, orig_height)
        new_width = int(orig_width * ratio)
        new_height = int(orig_height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Step 2: Binary search for optimal quality
    low, high = 10, 95
    best_quality = 85
    
    for _ in range(10):  # Max 10 iterations
        mid = (low + high) // 2
        
        # Save to bytes buffer to check size
        buffer = io.BytesIO()
        img.save(buffer, 'JPEG', quality=mid, optimize=True, progressive=True)
        size_kb = len(buffer.getvalue()) / 1024
        
        if size_kb <= target_kb:
            best_quality = mid
            low = mid + 1  # Try higher quality
        else:
            high = mid - 1  # Try lower quality
    
    # Step 3: Final save with best quality
    final_buffer = io.BytesIO()
    img.save(final_buffer, 'JPEG', quality=best_quality, optimize=True, progressive=True)
    
    # Step 4: If still too large, reduce dimensions
    final_size_kb = len(final_buffer.getvalue()) / 1024
    if final_size_kb > target_kb:
        # Further reduce dimensions
        reduction_factor = math.sqrt(target_kb / final_size_kb)
        new_width = int(img.width * reduction_factor * 0.9)
        new_height = int(img.height * reduction_factor * 0.9)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save again
        final_buffer = io.BytesIO()
        img.save(final_buffer, 'JPEG', quality=75, optimize=True, progressive=True)
        final_size_kb = len(final_buffer.getvalue()) / 1024
    
    return img, final_buffer.getvalue(), final_size_kb

def get_image_preview(img_data, max_size=300):
    """Create a base64 preview of image"""
    try:
        img = Image.open(io.BytesIO(img_data))
        img.thumbnail((max_size, max_size))
        
        buffer = io.BytesIO()
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        img.save(buffer, format='JPEG', quality=70)
        buffer.seek(0)
        
        return f"data:image/jpeg;base64,{base64.b64encode(buffer.read()).decode()}"
    except:
        # Return a placeholder if preview generation fails
        return "data:image/svg+xml;base64," + base64.b64encode(
            '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200" viewBox="0 0 300 200"><rect width="300" height="200" fill="#f0f0f0"/><text x="150" y="100" text-anchor="middle" fill="#666">Preview</text></svg>'.encode()
        ).decode()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/compress', methods=['POST'])
def compress_image():
    try:
        if 'image' not in request.files:
            return {'success': False, 'error': 'No image file provided'}
        
        file = request.files['image']
        target_kb = int(request.form.get('target_size', 15))
        
        if file.filename == '':
            return {'success': False, 'error': 'No selected file'}
        
        # Read original image
        original_data = file.read()
        
        # Check if file is actually an image
        try:
            original_img = Image.open(io.BytesIO(original_data))
            original_img.verify()  # Verify it's an image
            original_img = Image.open(io.BytesIO(original_data))  # Re-open after verify
        except:
            return {'success': False, 'error': 'Invalid image file'}
        
        # Get original stats
        original_size_kb = len(original_data) / 1024
        original_dimensions = f"{original_img.width}×{original_img.height}"
        
        # Compress image
        compressed_img, compressed_data, compressed_size_kb = smart_compress_to_target(
            original_img, target_kb
        )
        
        # Generate previews
        original_preview = get_image_preview(original_data)
        compressed_preview = get_image_preview(compressed_data)
        
        # Create base64 data for direct download
        compressed_base64 = f"data:image/jpeg;base64,{base64.b64encode(compressed_data).decode()}"
        
        # Generate filename
        original_name = file.filename
        name_without_ext = os.path.splitext(original_name)[0]
        filename = f"compressed_{name_without_ext[:20]}_{uuid.uuid4().hex[:8]}.jpg"
        
        return {
            'success': True,
            'original_size_kb': round(original_size_kb, 1),
            'compressed_size_kb': round(compressed_size_kb, 1),
            'original_dimensions': original_dimensions,
            'compressed_dimensions': f"{compressed_img.width}×{compressed_img.height}",
            'original_preview': original_preview,
            'compressed_preview': compressed_preview,
            'filename': filename,
            'compressed_data': compressed_base64,
            'compression_ratio': round(original_size_kb / compressed_size_kb, 1)
        }
        
    except Exception as e:
        import traceback
        print(f"Error in compress_image: {e}")
        print(traceback.format_exc())
        return {'success': False, 'error': f'Server error: {str(e)}'}

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up temporary files (optional endpoint)"""
    try:
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
        return {'success': True, 'message': 'Cleanup completed'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    # Clean up old files on startup
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
            except:
                pass
    
    print("🚀 Image Compressor Server Starting...")
    print("📍 Access at: http://127.0.0.1:5000")
    print("📁 Temp folder:", app.config['UPLOAD_FOLDER'])
    print("💡 Tip: Upload 200KB images and compress to 15KB!")
    print("📱 Pydroid 3 Compatible Version")
    
    app.run(debug=True, host='0.0.0.0', port=10000, threaded=True)
