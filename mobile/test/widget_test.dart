import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:proxyproof/main.dart';

void main() {
  testWidgets('ProxyProof smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: ProxyProofApp(),
      ),
    );
    expect(find.byType(ProxyProofApp), findsOneWidget);
  });
}
