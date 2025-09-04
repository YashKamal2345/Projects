import streamlit as st
import time
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load your model (make sure emotion_model.pkl is in same directory)
model = joblib.load("emotion_model.pkl")
keystrokes = []

# App UI
st.set_page_config(layout="wide")
st.title("🎭 Emotion Detection from Typing Patterns")
st.write("Type in the box below and click predict to see your emotion detected!")

# Track keystrokes
text_input = st.text_area("Start typing here...", height=200, key="text_input")

# Record timestamps when text changes
if text_input:
    keystrokes.append(time.time())

# Prediction function (same as your original)
def predict_emotion():
    if len(keystrokes) < 2:
        return "❌ Type more to get a prediction"
    delays = [keystrokes[i] - keystrokes[i-1] for i in range(1, len(keystrokes))]
    df = pd.DataFrame(delays, columns=["delay"])
    prediction = model.predict(df[["delay"]])
    return f"🧠 Detected Emotion: {prediction[0]}"

# Prediction button
if st.button("🔮 Predict Emotion"):
    result = predict_emotion()
    st.balloons()  # Simple celebration effect
    st.success(result)
    
    # Visualization (simpler than your particles but similar effect)
    fig, ax = plt.subplots()
    colors = np.random.rand(20, 3)
    sizes = 100 * np.random.rand(20)
    ax.scatter(np.random.rand(20), np.random.rand(20), c=colors, s=sizes, alpha=0.5)
    ax.set_axis_off()
    st.pyplot(fig)

st.markdown("---")
st.caption("Note: This analyzes typing rhythm patterns to predict emotion")
