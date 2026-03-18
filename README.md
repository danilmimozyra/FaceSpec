# **FaceSpec**

**FaceSpec** – Real-Time Face Analysis Application

**Author:** Lazurko Danylo

**Field of Study:** Operating systems and computer networks

---

# **Annotation**

This project focuses on developing an application for face analysis using artificial intelligence. The program detects faces and determines age, gender, and emotion. It supports real-time camera input, image processing, and video analysis. The goal was to create a simple, efficient, and user-friendly tool.

---

# **Introduction**

This project is focused on building a desktop application using computer vision and neural networks. Face analysis technologies are widely used today in areas such as security, marketing, and entertainment.

The main objective was to create an application that allows users to analyze faces in three different modes: camera, photo, and video. The program uses DeepFace for face analysis and OpenCV for image processing.

Special attention was given to performance optimization and user experience. The application is designed to be intuitive, responsive, and visually clear while maintaining acceptable processing speed.

---

# **Economic Analysis**

There are existing solutions such as Microsoft Azure Face API or Amazon Rekognition. These services are powerful but require internet access and are often paid.

The main advantage of this project is that it works locally, without external services. This improves privacy and removes operational costs.

The application could be used as a demonstration tool, educational project, or prototype. The return on investment is mainly educational, providing experience in neural networks and software development.

---

# **Development**

The application was developed in **Python** using the following technologies:

- **OpenCV** – image and video processing
- **DeepFace** – face analysis (age, gender, emotion)
- **Tkinter** – graphical interface
- **Pillow** – image handling

Project structure:

- `main.py` – main menu
- `camera.py` – real-time analysis
- `video.py` – video processing
- `photo.py` – image analysis
- `render_utils.py` – UI rendering

During development, several optimizations were implemented:

- image resizing
- asynchronous processing (threads)
- result caching

These improvements significantly increased performance.

---

# **Testing**

Five test scenarios were performed:

**1. Application startup**

The program launches correctly and displays the main menu.

**2. Camera mode**

Faces are detected in real time and attributes are displayed.

**3. Photo analysis**

Multiple faces are detected and analyzed correctly.

**4. Video analysis**

Video playback works with pause and frame navigation.

**5. Frame saving**

The user can save a frame with face annotations (without UI elements).

The application behaved as expected in all tests.

---

# **Deployment and Usage**

**Requirements:**

- **Python 3.9**
- **Libraries:**

```
pip install opencv-python deepface pillow
```

Run the application:

```
python main.py
```

---

# **License**

The project can be distributed under the **MIT License**, allowing free use and modification.

---

# **Git Repository**

GitHub link:

```
https://github.com/danilmimozyra/FaceSpec
```

---

# **Conclusion**

The project successfully demonstrates a face analysis application using neural networks. It provides real-time and offline processing in a simple interface.

During development, valuable experience was gained in performance optimization and UI design. Future improvements could include face recognition or better tracking.
