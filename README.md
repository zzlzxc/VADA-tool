# VADA-tool
*A Multicultural Benchmark and Evaluation Toolkit for Value-Aware Alignment in Large Language Models (LLMs)*  

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)]()

---

## 🌍 Overview
VADA is designed to evaluate how **Large Language Models (LLMs)** align with **diverse cultural and moral value systems**, spanning:

- **Chinese Socialist Core Values (SCV)**  
- **European Union Values (EUV)** 
- **Middle Eastern Values (MEV)** — Islamic ethical framework  

It provides:
- **Modular data generation pipeline** for scenarios and questions  
-  **Bayesian multi-model evaluation** integrating multiple LLM judges  
-  **Human-labeled validation subset (VADA-H700)**  
-  **Culturally grounded, regenerable benchmark (VADA-G)**  

---

## 🧰 Features
| Component               | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| `SceneGeneration.py`    | Generates culturally grounded scenarios covering 25 value dimensions |
| `QuestionGeneration.py` | Derives three types of probing questions: *role-playing*, *advisory*, *dilemma* |
| `AnswerGeneration.py`   | Creates responses for each scenario                          |
| `Eval.py`               | Implements **Bayesian ensemble evaluation** using multiple LLM evaluators (GPT-4o, Claude-3.5, DeepSeek-v3) |
| `pa.py`                 | Handles paraphrasing and similarity filtering                |

---

## 🏗️ Architecture
> The VADA framework consists of two major pipelines:
> 1️⃣ **Data Generation Pipeline** → Scenario + Question + Answer  
> 2️⃣ **Evaluation Pipeline** → Bayesian reliability-weighted ensemble



## 📦 Dataset 

The following JSON/JSONL files represent the main intermediate and final datasets in the VADA-tool pipeline.

---

### 🔹 1. `scenes.json`
**Produced by:** `SceneGeneration.py`  
**Purpose:** Defines culturally grounded **scenarios** under three value systems (SCV, EUV, MEV).

Each item describes a neutral moral or social situation.

### 🔹 2. `questions.jsonl`
**Produced by:** `QuestionGeneration.py`  
**Purpose:** Expands each scenario into one or more **natural questions** that can elicit culturally value-related reasoning.

### 🔹 3. `qa_annotation.jsonl`
**Produced by:** VADA-Bayes annotation (evaluation stage)  
**Purpose:** Stores **annotated alignment judgments** for generated question–answer pairs.

### 🔹 4. `sampled_700.jsonl`
Represents the **VADA-H700** validation benchmark (700 human-verified samples).

Used for model comparison, human agreement analysis, and reliability testing.


