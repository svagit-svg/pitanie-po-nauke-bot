# VK delivery records

VK uses its native postponed-post scheduler, independently of GitHub Actions.
`vk_plan_2026-11-06.json` contains one immediate post per community and 28 future
posts per community for 7–20 November 2026, 09:00 and 16:00 Europe/Moscow.
The plan starts after the previous known batch (Pitanie 185, Blizko 166).

`vk_delivery.json` records API-confirmed post IDs and scheduled dates. It contains
no access tokens. Do not clear this file to retry a failed batch.

Prepare a new dated plan with channel (`pitanie` or `blizko`), slug and optional
Unix `publish_date`. Check occupied slots and delivery history before sending.
The current community credentials cannot list postponed posts, so the journal
cannot detect posts scheduled manually or via other tools.

Validate the entire plan:

    python3 scripts/vk_refill.py data/PLAN.json

Send it:

    python3 scripts/vk_refill.py data/PLAN.json --send

Each intent is saved atomically before the API call; successful responses are
saved immediately with `post_id`. A repeated run skips confirmed deliveries.
After a timeout or an ambiguous response, the entry remains `pending`; the
script stops instead of blindly sending a duplicate. Check VK manually before
resolving that entry. Explicit API rejections are marked `rejected` and also
require review before a retry. HTTP requests are not automatically retried.

This is a finite buffer, not automatic generation or automatic replenishment.
Images are still added manually in VK. Telegram queues are independent.
