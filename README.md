# AudioIO

## Overview
AudioIO is a Python library designed for handling audio input and output streams with ease and flexibility. It simplifies the process of working with audio data in Python, providing a straightforward interface for both input and output operations.

## Features
- **Input Streams**: Capture audio data from various sources.
- **Output Streams**: Play and output audio data.
- **Audio Buffers**: Manage audio data efficiently.
- **Customizable Services**: Extend functionality according to specific needs.

## Requirements
- Python 3.x
- NumPy (1.26.3 or newer)

## Installation
To install AudioIO, you need to have Python installed on your system. The library also depends on NumPy. You can install the required packages using pip:
```
pip install numpy~=1.26.3
```

## Structure
- `base.py`: Base classes and functionalities.
- `buffers.py`: Handling of audio data buffers.
- `input_streams.py`: Classes and functions for audio input.
- `output_streams.py`: Classes and functions for audio output.
- `services.py`: Additional services and utilities.

## Getting Started
After installing the necessary packages, you can start using AudioIO in your Python projects. Here is a simple example of how to use AudioIO to capture audio from a microphone and play it back:

```python
# Example Python script using AudioIO
import AudioIO

# Initialize input and output streams
input_stream = AudioIO.input_streams.MicrophoneStream(chunk_size=512)
output_stream = AudioIO.output_streams.AudioPlaybackProcessor(chunk_size=input_stream.chunk_size, ...)

# Capture and play audio
for chunk in input_stream:
    output_stream.process(chunk)
```

## Contribution
Contributions to AudioIO are welcome! Feel free to fork the repository, make your changes, and submit a pull request.

## License
This project is licensed under the MIT License. For more information, please see the [LICENSE](LICENCE) file.
