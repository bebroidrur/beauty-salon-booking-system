# Простежуваність модуля Bookings

Ця таблиця є доповненням до [повної матриці ЛР5](traceability.md), а не заміною baseline matrix. У ній наведено лише п'ять реалізованих operationId Bookings.

| operationId | HTTP | REQ-ID | AC/GWT джерела | Фактичні тести |
| --- | --- | --- | --- | --- |
| `listBookings` | GET `/bookings` | F-009, F-010, F-030–033 | AC-009, AC-030, AC-033; GWT-019, GWT-029 | `test_ownership_and_roles`, `test_history_boundary`, contract success |
| `createBooking` | POST `/bookings` | F-008–029, F-055, F-056, F-059, F-060 | AC-009, 012, 015, 016, 018–029, 055, 056, 059, 060; GWT-001–014, GWT-018 | `test_create_snapshot`, `test_lead_boundary`, `test_work_interval`, `test_conflicts_and_adjacency`, `test_atomic_competition`, contract success |
| `getBooking` | GET `/bookings/{bookingId}` | F-009, F-010, F-031 | AC-009; GWT-019 | `test_ownership_and_roles`, `test_create_snapshot`, `test_history_boundary`, contract success |
| `updateBooking` | PATCH `/bookings/{bookingId}` | F-010, F-017, F-021–027, F-038–044, F-057, F-062–064 | AC-040–044, 057, 062–064; GWT-020–024, GWT-031–033 | `test_patch_snapshots`, `test_patch_rollback`, `test_protect_live_bookings`, notification tests, contract success |
| `cancelBooking` | POST `/bookings/{bookingId}/cancellation` | F-009, F-010, F-025, F-034–037, F-041, F-058, F-061 | AC-034–036, 041, 061; GWT-015–018, GWT-028, GWT-035 | `test_cancellation_boundary`, `test_history_boundary`, notification tests, contract success |

`GET /masters/{masterId}/slots` не належить до реалізованого скороченого Booking-модуля: він має окремий `listSlots` operationId, залежить від D-03 і залишений BLOCKED. Результати тестів беруться з фактичних журналів; таблиця не заявляє повного покриття всіх AC/GWT.
