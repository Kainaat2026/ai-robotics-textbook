---
id: chapter-12-conversational-robotics
title: Conversational Robotics & VLA Models
module: 4
week: 11
learning_objectives:
  - Understand Vision-Language-Action (VLA) model architecture
  - Implement natural language control for robots using foundation models
  - Use RT-2 and OpenVLA for language-conditioned policies
  - Integrate multimodal perception (vision + language)
  - Deploy conversational interfaces for human-robot interaction
estimated_time_minutes: 100
---

# Conversational Robotics & VLA Models

## Introduction

The integration of Large Language Models (LLMs) with robotics has created a new paradigm: **Conversational Robotics**. Vision-Language-Action (VLA) models combine visual perception, natural language understanding, and robotic action into unified architectures that can understand commands like "pick up the red mug and place it on the shelf" and execute them autonomously.

**Key Models:**
- **RT-2** (Google DeepMind): Robotics Transformer 2
- **OpenVLA** (OpenAI): Open-source VLA
- **PaLM-E** (Google): Embodied multimodal LLM
- **RoboFlamingo**: Vision-language model for manipulation

**Why VLA Models Matter:**
- Natural language control (no programming required)
- Generalization to novel objects and tasks
- Zero-shot and few-shot learning
- Human-like reasoning about the physical world

## VLA Architecture

### Overview

```
┌─────────────────────────────────────────────┐
│           Language Input (Text)             │
│      "Pick up the red mug on the table"     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│        Language Encoder (Transformer)       │
│         - BERT, GPT, T5, LLaMA              │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│           Vision Input (Images)             │
│     - RGB camera, depth, proprioception     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Vision Encoder (ViT/CNN)            │
│      - Vision Transformer, ResNet           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│      Multimodal Fusion (Cross-Attention)    │
│    - Combine vision and language features   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Action Decoder (Transformer)        │
│   - Autoregressively predict robot actions  │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│           Robot Actions (Output)            │
│   - Joint positions, gripper commands       │
└─────────────────────────────────────────────┘
```

### Key Components

1. **Language Encoder**: Processes text instructions into embeddings
2. **Vision Encoder**: Encodes visual observations (RGB, depth)
3. **Fusion Layer**: Combines vision and language via cross-attention
4. **Action Decoder**: Generates robot actions conditioned on multimodal input

## RT-2: Robotics Transformer 2

RT-2 treats robotic control as a sequence-to-sequence translation problem.

### RT-2 Architecture

```python
import torch
import torch.nn as nn
from transformers import T5EncoderModel, ViTModel

class RT2Model(nn.Module):
    """
    Simplified RT-2 architecture.

    RT-2 uses a Vision Transformer (ViT) for vision and T5 for language,
    combined with a Transformer decoder for action prediction.
    """

    def __init__(self, action_dim=7, hidden_dim=512):
        super().__init__()

        # Vision encoder (ViT)
        self.vision_encoder = ViTModel.from_pretrained('google/vit-base-patch16-224')

        # Language encoder (T5)
        self.language_encoder = T5EncoderModel.from_pretrained('t5-base')

        # Fusion layer (cross-attention)
        self.fusion = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=8,
            batch_first=True
        )

        # Projection layers
        self.vision_proj = nn.Linear(768, hidden_dim)  # ViT output dim
        self.language_proj = nn.Linear(768, hidden_dim)  # T5 output dim

        # Action decoder
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=hidden_dim,
            nhead=8,
            batch_first=True
        )
        self.action_decoder = nn.TransformerDecoder(decoder_layer, num_layers=6)

        # Action output head
        self.action_head = nn.Linear(hidden_dim, action_dim)

    def forward(self, images, text_input_ids, text_attention_mask):
        """
        Forward pass.

        Args:
            images: (batch, 3, 224, 224) - RGB images
            text_input_ids: (batch, seq_len) - Tokenized text
            text_attention_mask: (batch, seq_len) - Attention mask

        Returns:
            actions: (batch, action_dim) - Predicted robot actions
        """
        # Encode vision
        vision_output = self.vision_encoder(pixel_values=images)
        vision_features = vision_output.last_hidden_state  # (batch, num_patches, 768)
        vision_features = self.vision_proj(vision_features)  # (batch, num_patches, hidden_dim)

        # Encode language
        language_output = self.language_encoder(
            input_ids=text_input_ids,
            attention_mask=text_attention_mask
        )
        language_features = language_output.last_hidden_state  # (batch, seq_len, 768)
        language_features = self.language_proj(language_features)  # (batch, seq_len, hidden_dim)

        # Fusion: Cross-attention between vision and language
        fused_features, _ = self.fusion(
            query=vision_features,
            key=language_features,
            value=language_features
        )

        # Decode actions
        # Use fused features as memory for decoder
        action_query = fused_features.mean(dim=1, keepdim=True)  # (batch, 1, hidden_dim)
        action_features = self.action_decoder(
            tgt=action_query,
            memory=fused_features
        )

        # Predict actions
        actions = self.action_head(action_features.squeeze(1))  # (batch, action_dim)

        return actions

# Example usage
model = RT2Model(action_dim=7)

# Dummy inputs
batch_size = 4
images = torch.randn(batch_size, 3, 224, 224)
text_input_ids = torch.randint(0, 1000, (batch_size, 20))
text_attention_mask = torch.ones(batch_size, 20)

# Forward pass
actions = model(images, text_input_ids, text_attention_mask)
print(f"Predicted actions: {actions.shape}")  # (4, 7)
```

### Training RT-2

```python
import torch.optim as optim
from torch.utils.data import DataLoader

class RT2Trainer:
    """Train RT-2 model on robot demonstration data."""

    def __init__(self, model, device='cuda'):
        self.model = model.to(device)
        self.device = device
        self.optimizer = optim.AdamW(model.parameters(), lr=1e-4)
        self.criterion = nn.MSELoss()

    def train_epoch(self, dataloader):
        """Train for one epoch."""
        self.model.train()
        total_loss = 0

        for batch in dataloader:
            images = batch['images'].to(self.device)
            text_ids = batch['text_input_ids'].to(self.device)
            text_mask = batch['text_attention_mask'].to(self.device)
            target_actions = batch['actions'].to(self.device)

            # Forward pass
            predicted_actions = self.model(images, text_ids, text_mask)

            # Compute loss
            loss = self.criterion(predicted_actions, target_actions)

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(dataloader)

    def evaluate(self, dataloader):
        """Evaluate model."""
        self.model.eval()
        total_loss = 0

        with torch.no_grad():
            for batch in dataloader:
                images = batch['images'].to(self.device)
                text_ids = batch['text_input_ids'].to(self.device)
                text_mask = batch['text_attention_mask'].to(self.device)
                target_actions = batch['actions'].to(self.device)

                predicted_actions = self.model(images, text_ids, text_mask)
                loss = self.criterion(predicted_actions, target_actions)
                total_loss += loss.item()

        return total_loss / len(dataloader)

# Example training loop
trainer = RT2Trainer(model)

# Assuming you have a dataset
# train_dataset = RobotDataset(...)
# train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# for epoch in range(100):
#     train_loss = trainer.train_epoch(train_loader)
#     print(f"Epoch {epoch}: Loss = {train_loss:.4f}")
```

## OpenVLA

OpenVLA is an open-source Vision-Language-Action model.

### Using OpenVLA

```python
from transformers import AutoModel, AutoTokenizer
import torch

class OpenVLAController:
    """
    Controller using OpenVLA model.

    OpenVLA: Open-source VLA model trained on diverse robot datasets.
    """

    def __init__(self, model_name='openvla/openvla-7b'):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Load model and tokenizer
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model.eval()

    def predict_action(self, image, instruction):
        """
        Predict robot action from image and natural language instruction.

        Args:
            image: PIL Image or numpy array (H, W, 3)
            instruction: String instruction (e.g., "pick up the red block")

        Returns:
            action: 7D action (6D pose + gripper)
        """
        # Preprocess image
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Tokenize instruction
        text_inputs = self.tokenizer(
            instruction,
            return_tensors='pt',
            padding=True,
            truncation=True
        ).to(self.device)

        # Preprocess image (assuming model has image processor)
        # image_inputs = self.model.image_processor(image, return_tensors='pt').to(self.device)

        # Forward pass
        with torch.no_grad():
            # outputs = self.model(
            #     pixel_values=image_inputs['pixel_values'],
            #     input_ids=text_inputs['input_ids'],
            #     attention_mask=text_inputs['attention_mask']
            # )
            # action = outputs.actions[0].cpu().numpy()
            pass

        # Placeholder
        action = np.random.randn(7)

        return action

    def execute_instruction(self, robot, camera, instruction):
        """
        Execute natural language instruction on robot.

        Args:
            robot: Robot interface
            camera: Camera interface
            instruction: Natural language instruction
        """
        print(f"Executing: '{instruction}'")

        # Capture current observation
        image = camera.get_rgb_image()

        # Predict action
        action = self.predict_action(image, instruction)

        # Execute action on robot
        robot.execute_action(action)

        print("Action executed successfully!")

# Example usage
# vla = OpenVLAController()
# action = vla.predict_action(image, "pick up the blue cup")
# print(f"Predicted action: {action}")
```

## Multimodal Perception

### Fusing Vision and Language

```python
import torch
import torch.nn as nn

class MultimodalFusion(nn.Module):
    """
    Multimodal fusion module for combining vision and language.

    Techniques:
    1. Concatenation
    2. Cross-attention
    3. Gated fusion
    """

    def __init__(self, vision_dim=512, language_dim=512, hidden_dim=512):
        super().__init__()

        # Projection layers
        self.vision_proj = nn.Linear(vision_dim, hidden_dim)
        self.language_proj = nn.Linear(language_dim, hidden_dim)

        # Cross-attention
        self.cross_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=8,
            batch_first=True
        )

        # Gated fusion
        self.gate = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Sigmoid()
        )

        self.fusion_mlp = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

    def forward(self, vision_features, language_features):
        """
        Fuse vision and language features.

        Args:
            vision_features: (batch, num_patches, vision_dim)
            language_features: (batch, seq_len, language_dim)

        Returns:
            fused_features: (batch, hidden_dim)
        """
        # Project to common dimension
        vision_proj = self.vision_proj(vision_features)
        language_proj = self.language_proj(language_features)

        # Cross-attention: vision queries language
        attended_features, _ = self.cross_attention(
            query=vision_proj,
            key=language_proj,
            value=language_proj
        )

        # Pool vision and language
        vision_pooled = vision_proj.mean(dim=1)  # (batch, hidden_dim)
        language_pooled = language_proj.mean(dim=1)  # (batch, hidden_dim)

        # Gated fusion
        concat = torch.cat([vision_pooled, language_pooled], dim=1)
        gate = self.gate(concat)

        fused = gate * vision_pooled + (1 - gate) * language_pooled

        return fused
```

### Object Detection with Language Grounding

```python
class LanguageGroundedDetection:
    """
    Detect objects based on natural language descriptions.

    Example: "Find the red mug on the left side of the table"
    """

    def __init__(self, detector_model='owl-vit'):
        # OWL-ViT: Open-vocabulary object detector
        from transformers import OwlViTProcessor, OwlViTForObjectDetection

        self.processor = OwlViTProcessor.from_pretrained('google/owlvit-base-patch32')
        self.model = OwlViTForObjectDetection.from_pretrained('google/owlvit-base-patch32')

    def detect_with_text(self, image, text_queries):
        """
        Detect objects using text queries.

        Args:
            image: PIL Image
            text_queries: List of text descriptions (e.g., ["red mug", "blue bottle"])

        Returns:
            detections: List of bounding boxes and scores
        """
        # Preprocess
        inputs = self.processor(
            text=text_queries,
            images=image,
            return_tensors='pt'
        )

        # Detect
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Post-process
        target_sizes = torch.Tensor([image.size[::-1]])
        results = self.processor.post_process_object_detection(
            outputs=outputs,
            target_sizes=target_sizes,
            threshold=0.1
        )

        detections = []
        for i, text_query in enumerate(text_queries):
            boxes = results[0]['boxes'][i]
            scores = results[0]['scores'][i]

            for box, score in zip(boxes, scores):
                if score > 0.3:
                    detections.append({
                        'query': text_query,
                        'box': box.tolist(),
                        'score': score.item()
                    })

        return detections

# Example
# detector = LanguageGroundedDetection()
# detections = detector.detect_with_text(image, ["red mug", "laptop", "phone"])
# print(detections)
```

## Natural Language Task Planning

### LLM-based Task Planner

```python
import openai

class LLMTaskPlanner:
    """
    Use LLM to decompose high-level instructions into robot primitives.

    Example:
        Input: "Set the table for dinner"
        Output: ["pick plate", "place plate on table", "pick fork", ...]
    """

    def __init__(self, api_key):
        openai.api_key = api_key

        # Define robot primitives
        self.primitives = [
            "pick(object)",
            "place(object, location)",
            "move_to(location)",
            "open_gripper()",
            "close_gripper()",
            "navigate(location)"
        ]

    def plan_task(self, instruction):
        """
        Decompose high-level instruction into primitive actions.

        Args:
            instruction: Natural language instruction

        Returns:
            List of primitive actions
        """
        prompt = f"""You are a robot task planner. Given a high-level instruction, decompose it into a sequence of primitive robot actions.

Available primitives:
{', '.join(self.primitives)}

Instruction: {instruction}

Output a numbered list of primitive actions:"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a robot task planning assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )

        plan_text = response['choices'][0]['message']['content']

        # Parse plan
        actions = self.parse_plan(plan_text)

        return actions

    def parse_plan(self, plan_text):
        """Parse LLM output into structured actions."""
        lines = plan_text.strip().split('\n')
        actions = []

        for line in lines:
            # Remove numbering (e.g., "1. pick(object)" -> "pick(object)")
            line = line.strip()
            if line and line[0].isdigit():
                action = line.split('.', 1)[1].strip()
                actions.append(action)

        return actions

# Example
# planner = LLMTaskPlanner(api_key='your-openai-key')
# plan = planner.plan_task("Clean the kitchen table")
# print(plan)
# ['navigate(kitchen)', 'pick(sponge)', 'move_to(table)', 'wipe(table)', 'place(sponge, sink)']
```

## Building a Conversational Robot Interface

### Voice-Controlled Robot

```python
import speech_recognition as sr
import pyttsx3

class ConversationalRobotInterface:
    """
    Voice-controlled robot interface.

    Pipeline:
    1. Speech-to-text (speech recognition)
    2. NLP understanding (intent recognition)
    3. Task execution (robot controller)
    4. Text-to-speech feedback
    """

    def __init__(self, robot_controller):
        self.robot = robot_controller

        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Text-to-speech
        self.tts_engine = pyttsx3.init()

    def listen(self):
        """Listen for voice command."""
        with self.microphone as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        try:
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None

    def speak(self, text):
        """Speak text using TTS."""
        print(f"Robot says: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def understand_intent(self, text):
        """
        Extract intent from text.

        Simple keyword-based approach (can be replaced with NLU model).
        """
        text_lower = text.lower()

        if 'pick' in text_lower or 'grab' in text_lower:
            return {'intent': 'pick', 'object': self.extract_object(text)}
        elif 'place' in text_lower or 'put' in text_lower:
            return {'intent': 'place', 'location': self.extract_location(text)}
        elif 'move' in text_lower or 'go' in text_lower:
            return {'intent': 'navigate', 'location': self.extract_location(text)}
        else:
            return {'intent': 'unknown'}

    def extract_object(self, text):
        """Extract object name from text (simple approach)."""
        # In practice, use NER (Named Entity Recognition)
        words = text.lower().split()
        objects = ['cup', 'mug', 'bottle', 'phone', 'book']

        for obj in objects:
            if obj in words:
                return obj

        return 'object'

    def extract_location(self, text):
        """Extract location from text."""
        words = text.lower().split()
        locations = ['table', 'shelf', 'counter', 'box', 'floor']

        for loc in locations:
            if loc in words:
                return loc

        return 'location'

    def execute_command(self, intent):
        """Execute robot command based on intent."""
        if intent['intent'] == 'pick':
            obj = intent.get('object', 'object')
            self.speak(f"Picking up the {obj}")
            self.robot.pick_object(obj)

        elif intent['intent'] == 'place':
            loc = intent.get('location', 'location')
            self.speak(f"Placing object on the {loc}")
            self.robot.place_object(loc)

        elif intent['intent'] == 'navigate':
            loc = intent.get('location', 'location')
            self.speak(f"Moving to the {loc}")
            self.robot.navigate_to(loc)

        else:
            self.speak("I didn't understand that command")

    def run(self):
        """Main conversation loop."""
        self.speak("Hello! I'm ready to help. What would you like me to do?")

        while True:
            # Listen for command
            text = self.listen()

            if text is None:
                continue

            # Check for exit
            if 'stop' in text.lower() or 'exit' in text.lower():
                self.speak("Goodbye!")
                break

            # Understand intent
            intent = self.understand_intent(text)

            # Execute command
            self.execute_command(intent)

# Example usage
# robot = RobotController()
# interface = ConversationalRobotInterface(robot)
# interface.run()
```

## Deployment Considerations

### Optimizing VLA Models for Real-Time

```python
class VLADeployment:
    """Optimize VLA model for real-time robot control."""

    def __init__(self, model):
        self.model = model

    def quantize_model(self):
        """Apply INT8 quantization for faster inference."""
        import torch.quantization

        self.model.eval()
        quantized_model = torch.quantization.quantize_dynamic(
            self.model,
            {nn.Linear},
            dtype=torch.qint8
        )

        return quantized_model

    def compile_with_tensorrt(self):
        """Compile model with TensorRT for NVIDIA GPUs."""
        # Use torch2trt or ONNX -> TensorRT pipeline
        pass

    def measure_latency(self, num_trials=100):
        """Measure inference latency."""
        import time

        dummy_image = torch.randn(1, 3, 224, 224)
        dummy_text = torch.randint(0, 1000, (1, 20))
        dummy_mask = torch.ones(1, 20)

        latencies = []

        for _ in range(num_trials):
            start = time.time()
            with torch.no_grad():
                _ = self.model(dummy_image, dummy_text, dummy_mask)
            latency = time.time() - start
            latencies.append(latency)

        avg_latency = np.mean(latencies)
        print(f"Average latency: {avg_latency*1000:.2f} ms")

        return avg_latency
```

## Summary

- VLA models unify vision, language, and action for natural robot control
- RT-2 and OpenVLA enable language-conditioned robotic policies
- Multimodal fusion combines visual and linguistic understanding
- LLMs can decompose high-level tasks into robot primitives
- Conversational interfaces enable intuitive human-robot interaction
- Deployment requires optimization for real-time performance

## Exercises

1. Implement a simple VLA model that predicts actions from images and text
2. Use OpenVLA (or similar) to control a simulated robot with natural language
3. Build a language-grounded object detector using OWL-ViT
4. Create an LLM task planner that decomposes instructions into robot primitives
5. Develop a voice-controlled robot interface with speech recognition and TTS

## Next Chapter

In Chapter 13, we'll bring everything together in the Capstone Project - where you'll build a complete humanoid agent integrating ROS 2, simulation, AI models, and conversational interfaces.
