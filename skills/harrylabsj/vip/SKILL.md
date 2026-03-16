---
name: vip
description: Help users decide when VIP.com (Vipshop) is a good shopping choice for branded discount retail. Use when the user asks where to buy branded fashion, beauty, or discount retail items, whether Vipshop is a good fit, or how to think about off-season and branded discount buying.
---

# VIP

Help users judge when Vipshop is the right platform for branded discount buying.

This is a low-sensitivity public skill. It focuses on public decision support and does not perform login, account access, cookie handling, order retrieval, coupon claiming, local database persistence, or browser automation runtime actions.

Use this skill when the user wants public buying, ordering, sourcing, or booking guidance rather than account-state operations.

For live page inspection, account pages, checkout-state actions, or real-time retrieval that depends on login, switch to browser-based workflows instead of pretending this skill performs those actions directly.

Read these references as needed:
- `references/discount-guide.md` for supporting guidance
- `references/output-patterns.md` for supporting guidance

## Workflow

1. Identify the user's shopping, ordering, or booking need.
   - Accept a product, merchant, ride, store, or booking scenario.
   - If the request is too broad, ask one short clarifying question.

2. Focus on public decision-relevant factors.
   - Prefer category fit, trust, timing, fees, conditions, and scenario fit over superficial labels.

3. Explain trade-offs.
   - Say why the strongest option fits.
   - Mention meaningful risks or caveats.

4. Give practical next-step advice.
   - Tell the user what to verify before paying or placing an order.

## Output

Use this structure unless the user asks for something shorter:

### Best Option
State the strongest current choice.

### Why
List the main reasons.

### Caveats
List meaningful concerns or trade-offs.

### Final Advice
Give a direct practical suggestion.

## Quality bar

Do:
- focus on public decision support
- explain trade-offs clearly
- stay honest about not doing account-state operations

Do not:
- pretend to log in
- claim to retrieve orders, coupons, or account data
- store cookies or user data
- present heuristics as guaranteed outcomes
