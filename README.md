# Image Size Compressor 🖼️

A professional web-based image compression tool built with Flask and Pillow that reduces image sizes from 200KB to 15KB while maintaining visual quality.

## 🌟 Features

### Core Functionality
- **Smart Compression Algorithm**: Binary search optimization for precise target size control
- **Batch Processing Ready**: Easily extendable for multiple image processing
- **Cross-Platform**: Works on Windows, macOS, Linux, and mobile (Pydroid 3 compatible)

### User Interface
- **Modern & Responsive Design**: Clean, gradient-based UI with smooth animations
- **Drag & Drop Support**: Intuitive file upload interface
- **Real-time Preview**: Side-by-side comparison of original vs compressed images
- **Progress Indicators**: Visual feedback during compression process

### Technical Features
- **Dynamic Quality Adjustment**: Automatically adjusts compression parameters
- **Dimension Optimization**: Smart resizing for optimal file size
- **Multi-format Support**: Handles JPG, PNG, JPEG, BMP formats
- **Temporary File Management**: Secure handling of uploads with automatic cleanup

## 📋 Prerequisites

- Python 3.7 or higher
- pip package manager

## 🚀 Installation

### 1. Clone/Setup Project
```bash
# Create project directory
mkdir image-compressor
cd image-compressor

# Copy the Flask app code to app.py
```

### 2. Install Dependencies
```bash
pip install flask pillow
```

### 3. Run the Application
```bash
python app.py
```

## 🏗️ Project Structure

```
image-compressor/
│
├── app.py                    # Main Flask application
├── README.md                 # This documentation
├── requirements.txt          # Python dependencies
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file for configuration:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here

# File Upload Settings
MAX_CONTENT_LENGTH=5242880  # 5MB
UPLOAD_FOLDER=temp_uploads
ALLOWED_EXTENSIONS=jpg,jpeg,png,bmp

# Server Settings
HOST=0.0.0.0
PORT=5000
DEBUG=False
```

### Application Settings
Modifiable parameters in the code:

```python
# File size limits
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

# Compression defaults
DEFAULT_TARGET_SIZE = 15  # KB
MIN_TARGET_SIZE = 5       # KB
MAX_TARGET_SIZE = 200     # KB

# Image processing
MAX_DIMENSION = 1200      # pixels
PREVIEW_SIZE = 300        # pixels
```

## 📖 Usage Guide

### 1. Access the Web Interface
```
http://localhost:5000
```

### 2. Upload Image
- Drag & drop image file into the upload area
- Or click "Browse Files" to select manually
- Supported formats: JPG, PNG, JPEG, BMP
- Maximum file size: 5MB

### 3. Set Target Size
- Adjust target size using the slider (5-200 KB)
- Default: 15 KB (optimized for web usage)

### 4. Compress
- Click "Compress Image" button
- Wait for processing (visual progress indicator)

### 5. Download Result
- View side-by-side comparison
- Check file size reduction stats
- Click "Download Compressed Image"

## 🛠️ API Endpoints

### `GET /`
- **Description**: Main web interface
- **Response**: HTML page with upload form

### `POST /compress`
- **Description**: Compress uploaded image
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `image`: Image file (required)
  - `target_size`: Target size in KB (optional, default: 15)
- **Response**: JSON with compression results

### `POST /cleanup`
- **Description**: Clean temporary files
- **Response**: JSON with cleanup status

## 🔬 Compression Algorithm

### Smart Compression Process
1. **Format Conversion**: Convert all images to RGB format
2. **Dimension Optimization**: Resize if dimensions exceed 1200px
3. **Binary Search Quality Tuning**: Find optimal JPEG quality setting
4. **Final Optimization**: Apply progressive encoding and optimize flag

### Technical Details
```python
def smart_compress_to_target(img, target_kb=15):
    """
    1. Dimension reduction for large images
    2. Binary search for optimal quality (10-95 scale)
    3. Progressive encoding for better web performance
    4. Final size validation and adjustment
    """
```

## 📊 Performance Metrics

### Compression Results
- **Typical Reduction**: 50-90% file size reduction
- **Quality Retention**: Optimized visual quality
- **Speed**: < 2 seconds for average images
- **Memory Usage**: Minimal (stream-based processing)

### Supported Image Sizes
| Original Size | Target Size | Compression Ratio |
|--------------|-------------|-------------------|
| 200 KB       | 15 KB       | 13:1              |
| 100 KB       | 15 KB       | 6.7:1             |
| 50 KB        | 15 KB       | 3.3:1             |

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 🔒 Security Considerations

1. **File Upload Security**
   - File type validation
   - Size limit enforcement
   - MIME type checking

2. **Temporary File Management**
   - Auto-cleanup on startup
   - Secure temp directory usage
   - Session-based file handling

3. **Input Validation**
   - Target size boundaries
   - Image format verification
   - Error handling for malformed files

## 📱 Mobile Support

### Pydroid 3 Compatibility
- Tested and optimized for mobile Python development
- Lightweight memory usage
- Touch-friendly interface

### Responsive Design
- Mobile-first approach
- Touch gestures support
- Adaptive layouts

## 🧪 Testing

### Manual Testing
```bash
# Test compression with curl
curl -X POST -F "image=@test.jpg" -F "target_size=15" http://localhost:5000/compress
```

### Test Images
Include sample images in `test_images/` directory:
- `sample_200kb.jpg` - Test large file compression
- `sample_portrait.png` - Test format conversion
- `sample_landscape.bmp` - Test BMP to JPEG conversion

## 🔄 Future Enhancements

### Planned Features
- [ ] Batch image compression
- [ ] Additional format support (WebP, GIF)
- [ ] Advanced compression presets
- [ ] API key authentication
- [ ] Cloud storage integration
- [ ] Background processing queue

### Technical Improvements
- [ ] Async processing with Celery
- [ ] Redis caching for frequent requests
- [ ] CDN integration for global access
- [ ] Docker Compose setup

## 🐛 Troubleshooting

### Common Issues

1. **"File too large" error**
   - Solution: Ensure image is under 5MB limit
   - Check `MAX_CONTENT_LENGTH` setting

2. **Compressed size not reaching target**
   - Solution: Lower quality expectations for very small targets
   - Try slightly higher target size

3. **Memory errors on mobile**
   - Solution: Use smaller images
   - Restart application to clear temp files

### Debug Mode
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 coding standards
- Add comments for complex logic
- Include docstrings for all functions
- Update README for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask** - Lightweight web framework
- **Pillow (PIL)** - Image processing library
- **Pydroid 3** - Mobile Python IDE
- **Contributors** - All code contributors

## 📞 Support

For support, email [your-email] or create an issue in the GitHub repository.

---

**Made with ❤️ using Flask & Pillow**

*Convert 200KB images to 15KB effortlessly*