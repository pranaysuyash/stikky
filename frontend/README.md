# StickerCraft Frontend

Flutter mobile application for StickerCraft - AI-powered sticker creator.

## Features

- 🎨 Text-to-sticker generation
- 📸 Image-to-sticker conversion
- 🎭 Character maker with expressions
- ✨ Rich sticker editor
- 📱 Multi-platform export (WhatsApp, Telegram, Signal, iMessage)
- 💰 Credit-based monetization with RevenueCat

## Tech Stack

- **Framework**: Flutter 3.0+
- **State Management**: Riverpod
- **Navigation**: GoRouter
- **Networking**: Dio + Retrofit
- **Payments**: RevenueCat
- **Local Storage**: Hive + Shared Preferences

## Getting Started

### Prerequisites

- Flutter SDK 3.0 or higher
- Dart SDK 3.0 or higher
- Android Studio / Xcode (for mobile development)

### Installation

1. Install dependencies:
   ```bash
   flutter pub get
   ```

2. Run code generation (if needed):
   ```bash
   flutter pub run build_runner build
   ```

3. Run the app:
   ```bash
   flutter run
   ```

## Project Structure

```
lib/
├── core/
│   ├── router/          # Navigation configuration
│   ├── theme/           # App theming
│   └── constants/       # Constants and configs
├── screens/
│   ├── home/           # Home screen
│   ├── create/         # Sticker creation
│   ├── editor/         # Sticker editor
│   ├── export/         # Platform export
│   └── profile/        # User profile
├── widgets/            # Reusable widgets
├── services/           # API clients & services
├── models/             # Data models
└── main.dart           # App entry point
```

## Configuration

### API Endpoint

Update the API base URL in your configuration:

```dart
// lib/core/constants/api_constants.dart
const String API_BASE_URL = 'http://localhost:8000/api/v1';
```

### Environment Variables

For different environments (dev, staging, prod), use flavor configuration.

## Building for Production

### Android

```bash
flutter build appbundle --release
```

### iOS

```bash
flutter build ios --release
```

## Testing

Run tests:
```bash
flutter test
```

Run with coverage:
```bash
flutter test --coverage
```

## Code Style

Follow the Dart style guide and use `flutter analyze`:

```bash
flutter analyze
```

Format code:
```bash
dart format .
```

## Contributing

See [CONTRIBUTING.md](../docs/CONTRIBUTING.md) in the root directory.

## License

See [LICENSE](../LICENSE) in the root directory.
