# AI-Powered Smart Expense Tracker 📊🤖

A modern, full-stack financial dashboard that automates expense tracking by extracting structured data from unstructured receipt images using Computer Vision and Natural Language Processing.

Traditional expense trackers rely on tedious manual data entry. This application solves that by introducing an AI-powered receipt scanner with a human-in-the-loop verification system, alongside a fraud detection engine that prevents duplicate billing.

---

## ✨ Key Features

### 🧾 Intelligent Receipt Scanning
- Utilizes OpenCV for image preprocessing, including denoising and thresholding.
- Uses Tesseract OCR to extract raw text from uploaded receipt images.
- Enhances image quality to improve OCR accuracy.

### 🔍 Automated Data Parsing
- Custom regex-based pipelines extract:
  - Merchant Name
  - Transaction Date
  - Total Amount
- Automatically categorizes expenses using keyword-based heuristics.

### 🛡️ Fraud & Duplicate Detection
- Implements perceptual image hashing using ImageHash.
- Calculates Hamming distances between uploaded receipts.
- Detects and flags duplicate or visually similar receipts to maintain data integrity.

### 👨‍💻 Human-in-the-Loop Verification
- Allows users to review and edit AI-extracted information before saving.
- Ensures accuracy and reliability of financial records.

### 📈 Interactive Financial Dashboard
- Real-time KPI tracking:
  - Total Income
  - Total Expenses
  - Current Balance
- Dynamic daily and monthly analytics powered by Chart.js.

### 📊 One-Click Excel Export
- Generates formatted Excel reports using Pandas.
- Enables quick sharing and record management.

---

## 🛠️ Tech Stack

### Backend
- Python
- Flask
- SQLite

### AI & Computer Vision
- OpenCV
- Tesseract OCR (pytesseract)
- Pillow
- ImageHash

### Data Processing
- Pandas
- Regular Expressions (re)
- Python-dateutil

### Frontend
- HTML5
- CSS3 (Glassmorphism UI)
- Vanilla JavaScript
- Chart.js

---

## 📌 Resume Description

### Project Title
**AI-Powered Smart Expense Tracker**

### Technologies
**Python, Flask, OpenCV, Tesseract OCR, JavaScript, SQLite, Pandas**

### Resume Bullet Points

- Developed a full-stack financial management dashboard integrating an AI-powered receipt scanner to automate expense tracking and transaction categorization.
- Engineered a computer vision pipeline using OpenCV for image preprocessing (thresholding, denoising) to optimize receipt images for text extraction via Tesseract OCR.
- Designed a custom regex-based parsing engine to extract merchant, date, and amount information from OCR output while automating expense classification through keyword heuristics.
- Implemented a fraud detection system using perceptual image hashing and Hamming distance calculations to identify and flag duplicate receipt uploads.
- Built a responsive single-page application (SPA) featuring human-in-the-loop verification workflows and interactive financial visualizations using Chart.js.
- Architected RESTful Flask APIs integrated with SQLite for persistent transaction storage and leveraged Pandas to generate Excel-based financial reports.
