import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../widgets/enterprise_card.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _studentIdController = TextEditingController();
  final _passwordController = TextEditingController();
  String _role = 'student';
  bool _obscurePassword = true;

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _studentIdController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _submit() {
    final name = _nameController.text.trim();
    final email = _emailController.text.trim();
    final studentId = _studentIdController.text.trim();
    final password = _passwordController.text;

    if (name.isEmpty || email.isEmpty || password.isEmpty) return;
    if (_role == 'student' && studentId.isEmpty) return;

    ref.read(authProvider.notifier).register(
          name: name,
          email: email,
          password: password,
          role: _role,
          studentId: _role == 'student' ? studentId : null,
        );
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF09090B),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white, size: 20),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: const Text('Create Account', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 400),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    'Join ProxyProof',
                    style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold, letterSpacing: -0.5),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Self-register your institutional account and bind this device.',
                    style: TextStyle(color: Color(0xFFA1A1AA), fontSize: 12),
                  ),
                  const SizedBox(height: 24),

                  if (authState.error != null) ...[
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0x664C0519),
                        border: Border.all(color: const Color(0xFF881337)),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        authState.error!,
                        style: const TextStyle(color: Color(0xFFFECDD3), fontSize: 12),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],

                  EnterpriseCard(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const Text(
                          'ROLE',
                          style: TextStyle(color: Color(0xFF71717A), fontSize: 10, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                        ),
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            Expanded(
                              child: ChoiceChip(
                                label: const Center(child: Text('Student', style: TextStyle(fontSize: 12))),
                                selected: _role == 'student',
                                onSelected: (sel) => setState(() => _role = 'student'),
                                selectedColor: Colors.white,
                                labelStyle: TextStyle(
                                  color: _role == 'student' ? Colors.black : const Color(0xFFA1A1AA),
                                  fontWeight: FontWeight.bold,
                                ),
                                backgroundColor: const Color(0xFF18181B),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: ChoiceChip(
                                label: const Center(child: Text('Organizer', style: TextStyle(fontSize: 12))),
                                selected: _role == 'organizer',
                                onSelected: (sel) => setState(() => _role = 'organizer'),
                                selectedColor: Colors.white,
                                labelStyle: TextStyle(
                                  color: _role == 'organizer' ? Colors.black : const Color(0xFFA1A1AA),
                                  fontWeight: FontWeight.bold,
                                ),
                                backgroundColor: const Color(0xFF18181B),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),

                        const Text(
                          'FULL NAME',
                          style: TextStyle(color: Color(0xFF71717A), fontSize: 10, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                        ),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _nameController,
                          style: const TextStyle(color: Colors.white, fontSize: 13),
                          decoration: _inputDecoration('John Doe'),
                        ),
                        const SizedBox(height: 16),

                        const Text(
                          'EMAIL ADDRESS',
                          style: TextStyle(color: Color(0xFF71717A), fontSize: 10, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                        ),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _emailController,
                          keyboardType: TextInputType.emailAddress,
                          style: const TextStyle(color: Colors.white, fontSize: 13, fontFamily: 'monospace'),
                          decoration: _inputDecoration('john@university.edu'),
                        ),
                        const SizedBox(height: 16),

                        if (_role == 'student') ...[
                          const Text(
                            'STUDENT ID / ROLL NUMBER',
                            style: TextStyle(color: Color(0xFF71717A), fontSize: 10, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _studentIdController,
                            style: const TextStyle(color: Colors.white, fontSize: 13, fontFamily: 'monospace'),
                            decoration: _inputDecoration('STU-2026-999'),
                          ),
                          const SizedBox(height: 16),
                        ],

                        const Text(
                          'PASSWORD',
                          style: TextStyle(color: Color(0xFF71717A), fontSize: 10, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                        ),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _passwordController,
                          obscureText: _obscurePassword,
                          style: const TextStyle(color: Colors.white, fontSize: 13, fontFamily: 'monospace'),
                          decoration: _inputDecoration('••••••••••••').copyWith(
                            suffixIcon: IconButton(
                              icon: Icon(
                                _obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                                color: const Color(0xFF71717A),
                                size: 16,
                              ),
                              onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                            ),
                          ),
                        ),
                        const SizedBox(height: 24),

                        ElevatedButton(
                          onPressed: authState.isLoading ? null : _submit,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.white,
                            foregroundColor: Colors.black,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            elevation: 0,
                          ),
                          child: authState.isLoading
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black),
                                )
                              : const Text('Create Account & Sign In', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  InputDecoration _inputDecoration(String hint) {
    return InputDecoration(
      hintText: hint,
      hintStyle: const TextStyle(color: Color(0xFF52525B)),
      filled: true,
      fillColor: const Color(0xFF09090B),
      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(4),
        borderSide: const BorderSide(color: Color(0xFF27272A)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(4),
        borderSide: const BorderSide(color: Color(0xFF27272A)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(4),
        borderSide: const BorderSide(color: Color(0xFF71717A)),
      ),
    );
  }
}
