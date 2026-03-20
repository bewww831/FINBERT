# FinLens: AI-Powered Financial Advisor Bot

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-EE4C2C?logo=pytorch)](https://pytorch.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Tuned-FF6600?logo=python)](https://xgboost.readthedocs.io/)
[![FinBERT](https://img.shields.io/badge/FinBERT-Fine--tuned-FFD21E?logo=huggingface)](https://huggingface.co/project-aps/finbert-finetune)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](#testing)

_UoL BSc Computer Science CM3070 Final Project — Multi-modal AI investment recommendation system combining time-series forecasting, financial news sentiment analysis, and candlestick chart pattern recognition._

## 📖 Project Overview

Retail traders and individual investors lack access to affordable, transparent, and AI-powered financial advisory tools. Professional platforms like Bloomberg Terminal are prohibitively expensive, while free alternatives are unreliable, opaque, or narrowly focused on a single data source.

**FinLens** fills this gap:

- Combines **three independent AI models** operating on different data types into a unified recommendation.
- Implements a **transparent late fusion decision engine** — every recommendation shows exactly how each model contributed.
- Accessible through a **standard web browser** — no special hardware or software required.

⚡ **Impact:** Turns multi-signal financial analysis that was previously only available to institutional investors into a free, explainable, web-based tool for everyday traders.

## ✨ Key Features

- **🤖 Multi-Modal AI Fusion**
  - XGBoost: time-series price forecasting over a 21-day horizon
  - Fine-tuned FinBERT: financial news sentiment classification
  - ResNet-18 CNN: candlestick chart pattern recognition

- **🔢 Transparent Decision Engine**
  Late fusion weighted formula — every score is visible to the user:
