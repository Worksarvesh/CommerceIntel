import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import os

def train_churn_model(rfm_path, output_dir="docs/plots", model_path="models/churn_model.pkl"):
    rfm = pd.read_csv(rfm_path)
    
    # Define Churn: Customers who haven't purchased in the last 90 days (Recency > 90)
    # This is a simplified proxy for churn in non-subscription retail
    rfm['Churn'] = (rfm['Recency'] > 90).astype(int)
    
    X = rfm[['Recency', 'Frequency', 'Monetary']]
    y = rfm['Churn']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest for Churn Prediction...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix - Churn Prediction')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f"{output_dir}/churn_confusion_matrix.png")
    plt.close()
    
    # Feature Importance
    importances = model.feature_importances_
    plt.figure(figsize=(10, 6))
    plt.bar(X.columns, importances)
    plt.title('Feature Importance for Churn')
    plt.savefig(f"{output_dir}/churn_feature_importance.png")
    plt.close()
    
    # Save Model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Churn model saved to {model_path}")

if __name__ == "__main__":
    train_churn_model("data/rfm_data.csv")
