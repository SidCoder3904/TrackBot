# TrackBot

TrackBot is an advanced robotic system designed to locate, track, and follow a target using monocular depth perception. The project leverages Python, OpenCV, MediaPipe, and Arduino to create a droid with real-time tracking capabilities, achieving over 90% accuracy in servo motor movements and precise 3-D trajectory mapping. A detailed ppt and demonstration video has been provided for project overview in the repo

## Features

- **Real-Time Tracking:** Utilizes OpenCV and MediaPipe to detect and track a hand as the target.
- **Servo Motor Control:** Integrates Arduino to control servo motors for precise camera adjustments.
- **Multithreading:** Implements multithreading to ensure real-time, lag-free performance.
- **Target Locking:** Auto-target-locking with visual feedback on the camera feed.
- **Depth Perception:** Computes the 3-D trajectory of the target for accurate movement.

## Components

- **Python**: Core programming language used for control and processing.
- **OpenCV**: Library for image processing and object detection.
- **MediaPipe**: Framework for hand tracking.
- **Arduino**: Microcontroller for servo motor control.
- **Servo Motors**: For adjusting the camera’s horizontal and vertical angles.
- **Laser**: Provides enhanced targeting precision.
