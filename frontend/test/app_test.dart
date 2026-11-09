import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:orvexa/app/app.dart';

void main() {
  testWidgets('application starts on the ORVEXA home screen', (tester) async {
	await tester.pumpWidget(const ProviderScope(child: OrvexaApp()));

	expect(find.text('ORVEXA'), findsWidgets);
	expect(find.text('Understand More. Act Smarter.'), findsOneWidget);
  });

  testWidgets('settings navigation opens the settings screen', (tester) async {
	await tester.pumpWidget(const ProviderScope(child: OrvexaApp()));
	await tester.tap(find.byTooltip('Settings'));
	await tester.pumpAndSettle();

	expect(find.text('Settings'), findsOneWidget);
	expect(find.text('Appearance'), findsOneWidget);
  });

  testWidgets('light and dark themes are configured', (tester) async {
	await tester.pumpWidget(const ProviderScope(child: OrvexaApp()));
	final materialApp = tester.widget<MaterialApp>(find.byType(MaterialApp));

	expect(materialApp.theme?.brightness, Brightness.light);
	expect(materialApp.darkTheme?.brightness, Brightness.dark);
  });
}
