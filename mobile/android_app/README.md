# KIT CampusAI Mobile App

Flutter-based mobile application for KIT CampusAI knowledge base chatbot.

## Features

- **Google Sign-In** - Secure authentication with Google OAuth
- **Knowledge Base Chat** - AI-powered Q&A about KIT campus
- **Real-time Responses** - Fast responses powered by Gemini AI
- **Source Citations** - View sources for AI responses
- **Chat History** - Access previous conversations
- **Material Design** - Modern UI with Material 3

## Prerequisites

- Flutter SDK 3.0+
- Android Studio / VS Code
- Android device or emulator (API 21+)
- Google Cloud Console project with OAuth configured

## Setup

### 1. Install Dependencies

```bash
flutter pub get
```

### 2. Configure Google Sign-In

#### Android Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sign-In API
4. Create OAuth 2.0 credentials:
   - Application type: Android
   - Get SHA-1 fingerprint: `keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android`
   - Package name: `com.kitcampusai.android_app`

5. Download `google-services.json` and place in `android/app/`

6. Add to `android/app/build.gradle`:
```gradle
apply plugin: 'com.google.gms.google-services'

dependencies {
    implementation 'com.google.firebase:firebase-bom:32.0.0'
}
```

### 3. Update API Base URL

Edit `lib/services/api_service.dart` and `lib/services/auth_service.dart`:

```dart
static const String _baseUrl = 'https://your-api-url.com/api/v1';
```

For Android emulator, use:
```dart
static const String _baseUrl = 'http://10.0.2.2:8000/api/v1';
```

### 4. Run the App

```bash
flutter run
```

## Project Structure

```
lib/
├── models/           # Data models
│   ├── user_model.dart
│   └── message_model.dart
├── services/         # API and auth services
│   ├── auth_service.dart
│   └── api_service.dart
├── screens/          # UI screens
│   ├── splash_screen.dart
│   ├── login_screen.dart
│   ├── home_screen.dart
│   └── chat_screen.dart
├── widgets/          # Reusable widgets
└── main.dart         # App entry point
```

## Building for Release

### Android APK

```bash
flutter build apk --release
```

APK location: `build/app/outputs/flutter-apk/app-release.apk`

### Android App Bundle (for Play Store)

```bash
flutter build appbundle --release
```

AAB location: `build/app/outputs/bundle/release/app-release.aab`

## Testing

```bash
flutter test
```

## Troubleshooting

### Google Sign-In Not Working
- Verify SHA-1 fingerprint is correct
- Check package name matches OAuth credentials
- Ensure `google-services.json` is in correct location

### API Connection Issues
- Check base URL in service files
- For emulator, use `10.0.2.2` instead of `localhost`
- Verify backend is running and accessible

### Build Errors
```bash
flutter clean
flutter pub get
flutter run
```

## License

MIT License
