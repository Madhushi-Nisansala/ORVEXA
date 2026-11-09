import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:orvexa/app/app.dart';

void main() {
  testWidgets('renders the ORVEXA foundation home screen', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: OrvexaApp()));

    expect(find.text('ORVEXA'), findsNWidgets(2));
    expect(find.text('Understand More. Act Smarter.'), findsOneWidget);
    expect(find.text('Backend status'), findsOneWidget);
  });
}
