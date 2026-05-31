AI-Powered Smart Expense Tracker 📊🤖
A modern, full-stack financial dashboard that automates expense tracking by extracting structured data from unstructured receipt images using Computer Vision and Natural Language Processing.

Traditional expense trackers rely on tedious manual data entry. This application solves that by introducing an AI receipt scanner with a "human-in-the-loop" verification system, alongside a robust fraud detection engine that prevents duplicate billing.

✨ Key Features
Intelligent Receipt Scanning: Utilizes OpenCV for image preprocessing (denoising, thresholding) and Tesseract OCR to extract raw text from uploaded bills.

Automated Data Parsing: Custom regex pipelines parse unstructured OCR text to accurately identify Merchants, Dates, Totals, and automatically categorize expenses based on keyword heuristics.

Fraud & Duplicate Detection: Implements perceptual image hashing (imagehash) to calculate Hamming distances between uploads, instantly flagging duplicate or visually identical receipts to ensure financial data integrity.

Human-in-the-Loop Verification: Seamless UI flow that allows users to review and correct AI-extracted data before committing it to the database.

Interactive Financial Dashboard: Real-time KPI tracking (Income, Expense, Balance) with dynamic Monthly/Daily charting powered by Chart.js.

One-Click Export: Generates clean, formatted Excel reports of all transactions using the Pandas library.

🛠️ Tech Stack
Backend: Python, Flask, SQLite

AI & Computer Vision: OpenCV, Tesseract OCR (pytesseract), Pillow, ImageHash

Data Processing: Pandas, Regex (re), Python-dateutil

Frontend: HTML5, CSS3 (Modern Glassmorphism UI), Vanilla JavaScript, Chart.js

For Your Resume
For a resume, you need punchy, action-oriented bullet points that focus on your technical achievements, the algorithms used, and the impact of the features.

Project Title: AI-Powered Smart Expense Tracker
Technologies: Python, Flask, OpenCV, Tesseract OCR, JavaScript, SQLite, Pandas

Developed a full-stack financial management dashboard integrating an AI-driven receipt scanner to automate manual data entry and categorize transactions.

Engineered a computer vision pipeline using OpenCV for image preprocessing (thresholding, denoising) to optimize unstructured receipt images for text extraction via Tesseract OCR.

Designed a custom regex-based parsing engine to extract precise data points (Merchant, Date, Amount) from raw OCR output, combined with keyword heuristics for automated expense classification.

Implemented a robust fraud detection system utilizing perceptual image hashing to calculate Hamming distances, successfully identifying and flagging duplicate receipt uploads to maintain data integrity.

Built a responsive Single Page Application (SPA) using Vanilla JavaScript and CSS, featuring a "human-in-the-loop" data verification UI and real-time financial data visualization using Chart.js.

Architected a RESTful Flask API integrated with a SQLite database for persistent storage, and utilized Pandas to enable one-click generation of Excel-formatted financial reports.
