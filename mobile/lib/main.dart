import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'config/app_config.dart';
import 'providers/auth_provider.dart';
import 'screens/login_screen.dart';
import 'screens/student_home_screen.dart';
import 'screens/organizer_home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppConfig.init();
  runApp(
    const ProviderScope(
      child: ProxyProofApp(),
    ),
  );
}

class ProxyProofApp extends ConsumerWidget {
  const ProxyProofApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    return MaterialApp(
      title: 'ProxyProof',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF09090B),
        colorScheme: const ColorScheme.dark(
          primary: Colors.white,
          secondary: Color(0xFF34D399),
          surface: Color(0xFF121214),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF0C0C0E),
          elevation: 0,
        ),
      ),
      home: authState.isLoading
          ? const Scaffold(
              backgroundColor: Color(0xFF09090B),
              body: Center(
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Color(0xFF34D399),
                ),
              ),
            )
          : authState.user == null
              ? const LoginScreen()
              : authState.user!.isOrganizer
                  ? const OrganizerHomeScreen()
                  : const StudentHomeScreen(),
    );
  }
}
