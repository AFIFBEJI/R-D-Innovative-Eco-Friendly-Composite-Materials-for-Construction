# Innovative Eco-Friendly Composite Materials for Construction

## 📜 Research Proposal

### Overview

This research aims to develop innovative and environmentally friendly composite materials for the construction industry. The core of the project involves utilizing two types of waste to manufacture cement mortars suitable for general construction and ecological paving blocks. We will employ **Response Surface Methodology (RSM)** to predict and optimize the physical and mechanical properties of these novel mortars.

**Project ID:** R&D Eco-materials #N°1

---

### Project Personnel

* **Supervisors:**
    * **Taheni Kallel, Eng., PhD.**
        * *Role:* Assistant Professor & Project Supervisor
        * *Institution:* ESPRIT, School of Engineers
    * **Afif Beji, Eng., M.Sc.**
        * *Role:* Assistant Professor & Project Co-Supervisor
        * *Institution:* ESPRIT, School of Engineers
* **Intern:**
    * **Gilles Aubin Ndambwe**
        * *Role:* Final Year Engineering Student
        * *Institution:* ESPRIT, School of Engineers

---

### Materials

The primary components for this study include:
- **Aggregates:** Two types of construction sand from different origins (S1, S2) and recycled sand (SR) derived from crushed demolition waste.
- **Reinforcement:** Polymerized polyethylene terephthalate (PET) fibers of varying lengths (10mm, 20mm, 30mm) sourced from packaging straps.
- **Binders:** CEM I or II, 42.5 R cement and hydraulic lime as a partial substitute.
- **Additives:** Natural vegetable fibers to enhance specific properties.

### Research Objectives

The study will evaluate the material's performance based on key engineering criteria:
- **Physical Properties:** Air content, water absorption (WA), and shrinkage (Sh).
- **Mechanical Properties:** Flexural strength (Rf) and compressive strength (Rc).

Additionally, the chemical and mineralogical composition of all raw materials will be analyzed to understand their interactions within the cementitious matrix. The mechanical behavior of the PET fibers will also be assessed through tensile tests.

### Methodology

A **Box-Behnken experimental design** will be used as the foundation for developing an **Analysis of Variance (ANOVA)**. This statistical approach will help predict and optimize the output responses based on the input variables. The entire data processing and analysis workflow will be managed using **Python** and its scientific computing libraries.

---

## 💻 Numerical Simulations

This section outlines the computational framework for predicting and optimizing the properties of the composite materials.

### Objectives
- Develop robust predictive models for material properties using **Response Surface Methodology (RSM)**.
- Implement a **Box-Behnken design** to systematically explore the variable space and find optimal compositions.
- Perform rigorous statistical analysis using **ANOVA** to validate the models.
- Create powerful visualization tools to analyze experimental data and simulation results.

### Simulation Components
- **Response Surface Modeling:** Implementation of second-order polynomial regression models to map the relationship between input factors and output responses.
- **Material Property Prediction:** Dedicated models for predicting compressive strength, flexural strength, water absorption, and shrinkage.
- **Statistical Analysis:** Calculation of key metrics like R², adjusted R², and p-values to assess model significance and perform residual analysis.
- **Optimization:** Utilization of a desirability function approach for multi-objective optimization to find the best balance of material properties.

---

## ✨ Graphical User Interface (GUI)

To enhance user experience and streamline the research process, a modern and intuitive Graphical User Interface (GUI) will be developed using the **CustomTkinter** library in Python.



### Features
- **Data Input Module:** User-friendly forms for inputting material compositions and experimental parameters, with support for batch data import from CSV/Excel files.
- **Experimental Design Generator:** A tool to automatically generate a Box-Behnken design matrix based on user-defined factors and levels.
- **Data Analysis Dashboard:** An interactive dashboard to perform RSM analysis, view ANOVA tables, and validate predictive models in real-time.
- **Visualization Tools:**
    - Interactive 2D contour plots and 3D surface plots to visualize the design space.
    - Residual plots and comparison charts for model diagnostics.
- **Optimization Interface:** A dedicated module for defining constraints and running multi-objective optimization to find the ideal material composition.
- **Report Generation:** Automated creation and export of results, graphs, and logs to PDF or Excel formats.

### User Experience Enhancements
- **Modern Design:** A clean, professional interface with options for light and dark themes.
- **Responsive Layout:** The application window will be fully responsive and adapt to different screen sizes.
- **Real-time Feedback:** Progress indicators and notifications for long-running computations.
- **Built-in Help:** Integrated documentation and tooltips to guide the user.

---

## 🚀 Installation and Usage

### Prerequisites
- Python 3.8 or higher

### Dependencies
Install the required libraries using pip:
```bash
pip install numpy pandas scipy matplotlib seaborn scikit-learn
pip install customtkinter pillow openpyxl xlrd pyDOE2
```

### Quick Start
1.  **Clone the repository (replace with your final URL):**
    ```bash
    git clone [https://github.com/AFIFBEJI/R-D-Innovative-Eco-Friendly-Composite-Materials-for-Construction.git](https://github.com/AFIFBEJI/R-D-Innovative-Eco-Friendly-Composite-Materials-for-Construction.git)
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd R-D-Innovative-Eco-Friendly-Composite-Materials-for-Construction
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the GUI application:**
    ```bash
    python main_gui.py
    ```

---

## 📁 Project Structure
```
├── data/
│   ├── raw_materials/
│   └── experimental_results/
├── src/
│   ├── simulations/
│   │   ├── rsm_analysis.py
│   │   └── optimization.py
│   ├── gui/
│   │   ├── main_window.py
│   │   ├── input_frame.py
│   │   └── visualization_frame.py
│   └── utils/
│       └── data_processing.py
├── tests/
├── docs/
├── requirements.txt
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue.

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

## 📞 Contact

- **Institution:** ESPRIT-TECH
- **Laboratory:** Civil Engineering Laboratory
- **Location:** Tunisia

## 🙏 Acknowledgments

- **ESPRIT-TECH** for providing the laboratory facilities and support.
- Our partner cement plants and material suppliers.
```
