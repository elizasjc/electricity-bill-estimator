# ⚡ Electricity Bill Estimator

An offline web-based application that helps users estimate their monthly electricity bill based on appliance usage. The system allows appliance-level input, calculates energy consumption and cost, and provides visual insights like bar, pie, and bubble charts. User history is stored locally to help track consumption trends over time.

---

## 🚀 Features

- 🔐 User Login & Registration (Offline)
- 📦 Appliance-wise quantity and daily usage input
- ⚙️ Automatic bill estimation based on usage and appliance ratings
- 📊 Visualizations: Bar, Pie, Bubble charts
- 📈 Personalized usage history and trend detection
- 🧠 Insights like most energy-consuming appliance
- 🗃️ Local database using SQLite for persistence

---

## 🖥️ Technologies Used

- Python (Flask Framework)
- HTML, CSS (Bootstrap)
- Jinja2 (Flask templates)
- Matplotlib (for visualizations)
- SQLite (as a local DB)
- JavaScript (for dynamic form behavior)

---

## 🔧 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/elizasjc/electricity-bill-estimator.git
   cd electricity-bill-estimator

2.  Install required packages
    bash
    pip install -r requirements.txt

3.  Run the application
    bash
    python app.py

4.  Open your browser and go to:
    bash
    http://localhost:5000


🧪 How to Use
-Register or log in with a username and password.
-Enter quantity and usage hours for each listed appliance.
-Select the number of billing days and a chart type (bar, pie, bubble).
-Submit to view:
-⚡ Total energy consumed (in kWh)
-💸 Estimated electricity bill
-📊 Visualizations and appliance-level breakdown
-📈 Usage trend history and change comparison


##📷 Screenshots
-![Register](<Screenshot 2025-06-27 134514.png>)
-![Login](<Screenshot 2025-06-27 134458.png>)
-![Input](<Screenshot 2025-06-27 134619.png>)
-![Estimation](<Screenshot 2025-06-27 134639.png>)
-![Visual](<Screenshot 2025-06-27 134658.png>)
-![Usage History Visual](<Screenshot 2025-06-27 134725.png>)
-![Usage History](<Screenshot 2025-06-27 134800.png>)

## 🔮 Future Enhancements
-Export results to PDF
-Add dark mode toggle
-Allow saving multiple usage profiles
-Add admin analytics dashboard
-Enable cloud sync with login (Firebase, etc.)

## 🗃️ Database Structure
-SQLite Database: users.db
-users table:
-id (INT, Primary Key)
-username (TEXT, unique)
-password (TEXT, hashed)
-usage_history table:
-id (INT, Primary Key)
-username (TEXT)
-timestamp (TEXT)
-appliance_data (TEXT – JSON)
-total_energy (REAL)
-estimated_bill (REAL)

## 👩‍💻 Author
-Shilpa J Chethalen
-Postgraduate Student – M.Sc. Data Science
-GitHub: elizasjc
