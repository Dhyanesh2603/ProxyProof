import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/device_info_service.dart';
import '../widgets/enterprise_card.dart';

class DeviceRegistrationScreen extends StatefulWidget {
  const DeviceRegistrationScreen({super.key});

  @override
  State<DeviceRegistrationScreen> createState() => _DeviceRegistrationScreenState();
}

class _DeviceRegistrationScreenState extends State<DeviceRegistrationScreen> {
  final ApiService _api = ApiService();
  final DeviceInfoService _deviceInfo = DeviceInfoService();

  bool _loading = true;
  Map<String, dynamic>? _boundDevice;
  Map<String, String>? _currentHardware;

  final _reasonController = TextEditingController();
  final _newModelController = TextEditingController();
  bool _submitting = false;
  String? _message;
  bool _isSuccess = false;

  @override
  void initState() {
    super.initState();
    _loadDevice();
  }

  @override
  void dispose() {
    _reasonController.dispose();
    _newModelController.dispose();
    super.dispose();
  }

  Future<void> _loadDevice() async {
    setState(() => _loading = true);
    try {
      final myDev = await _api.getMyDevice();
      final curHw = await _deviceInfo.getDeviceInfo();
      setState(() {
        _boundDevice = myDev['device'];
        _currentHardware = curHw;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Future<void> _submitChangeRequest() async {
    final reason = _reasonController.text.trim();
    final modelName = _newModelController.text.trim().isEmpty ? (_currentHardware?['name'] ?? 'New Phone') : _newModelController.text.trim();
    final newUuid = _currentHardware?['uuid'] ?? 'DEV-NEW-${DateTime.now().millisecondsSinceEpoch}';

    if (reason.isEmpty) {
      setState(() {
        _message = 'Please provide a clear reason for the device change.';
        _isSuccess = false;
      });
      return;
    }

    setState(() {
      _submitting = true;
      _message = null;
    });

    try {
      await _api.requestDeviceChange(newUuid, modelName, reason);
      setState(() {
        _submitting = false;
        _isSuccess = true;
        _message = 'Device migration request submitted! An organizer will review and approve it.';
        _reasonController.clear();
      });
    } catch (e) {
      setState(() {
        _submitting = false;
        _isSuccess = false;
        _message = e.toString().replaceAll('Exception: ', '');
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF09090B),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0C0C0E),
        elevation: 0,
        title: const Text(
          'Device Hardware Binding',
          style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF34D399)))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Currently bound device card
                  EnterpriseCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.lock_outline, size: 14, color: Color(0xFF34D399)),
                            SizedBox(width: 6),
                            Text(
                              'BOUND AUTHORIZED DEVICE',
                              style: TextStyle(
                                color: Color(0xFF34D399),
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                fontFamily: 'monospace',
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Text(
                          _boundDevice != null ? (_boundDevice!['device_name'] ?? 'Mobile Phone') : 'No device bound yet',
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _boundDevice != null ? _boundDevice!['device_uuid'] : (_currentHardware?['uuid'] ?? 'N/A'),
                          style: const TextStyle(color: Color(0xFF71717A), fontSize: 11, fontFamily: 'monospace'),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'One student is bound to exactly one physical device. Submitting attendance from another phone is blocked by the anti-proxy engine.',
                          style: TextStyle(color: Color(0xFFA1A1AA), fontSize: 11),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Request Device Change Section
                  const Text(
                    'REQUEST DEVICE MIGRATION',
                    style: TextStyle(color: Color(0xFF71717A), fontSize: 11, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                  ),
                  const SizedBox(height: 10),

                  EnterpriseCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        if (_message != null) ...[
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: _isSuccess ? const Color(0xFF022C22) : const Color(0xFF4C0519),
                              border: Border.all(color: _isSuccess ? const Color(0xFF064E3B) : const Color(0xFF881337)),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              _message!,
                              style: TextStyle(color: _isSuccess ? const Color(0xFF6EE7B7) : const Color(0xFFFECDD3), fontSize: 11),
                            ),
                          ),
                          const SizedBox(height: 14),
                        ],

                        const Text(
                          'NEW DEVICE MODEL (OPTIONAL)',
                          style: TextStyle(color: Color(0xFF71717A), fontSize: 10, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                        ),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _newModelController,
                          style: const TextStyle(color: Colors.white, fontSize: 12),
                          decoration: InputDecoration(
                            hintText: _currentHardware?['name'] ?? 'e.g. iPhone 15 Pro, Pixel 8',
                            hintStyle: const TextStyle(color: Color(0xFF52525B)),
                            filled: true,
                            fillColor: const Color(0xFF09090B),
                            contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(4),
                              borderSide: const BorderSide(color: Color(0xFF27272A)),
                            ),
                            enabledBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(4),
                              borderSide: const BorderSide(color: Color(0xFF27272A)),
                            ),
                          ),
                        ),
                        const SizedBox(height: 14),

                        const Text(
                          'REASON FOR DEVICE CHANGE',
                          style: TextStyle(color: Color(0xFF71717A), fontSize: 10, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                        ),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _reasonController,
                          maxLines: 3,
                          style: const TextStyle(color: Colors.white, fontSize: 12),
                          decoration: InputDecoration(
                            hintText: 'e.g. Damaged previous screen, upgraded personal phone...',
                            hintStyle: const TextStyle(color: Color(0xFF52525B)),
                            filled: true,
                            fillColor: const Color(0xFF09090B),
                            contentPadding: const EdgeInsets.all(10),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(4),
                              borderSide: const BorderSide(color: Color(0xFF27272A)),
                            ),
                            enabledBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(4),
                              borderSide: const BorderSide(color: Color(0xFF27272A)),
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),

                        ElevatedButton(
                          onPressed: _submitting ? null : _submitChangeRequest,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.white,
                            foregroundColor: Colors.black,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                            padding: const EdgeInsets.symmetric(vertical: 10),
                            elevation: 0,
                          ),
                          child: _submitting
                              ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
                              : const Text('Submit Migration Request', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
