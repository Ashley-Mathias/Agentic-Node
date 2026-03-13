# Test IDs (TestSprite / data-testid)

Stable `data-testid` attributes for UI automation and TestSprite selector healing. Use these selectors in tests (e.g. `[data-testid="new-chat-btn"]`) instead of IDs or classes that may change.

## Chat app (`index.html`)

| Test ID | Element | Description |
|---------|---------|-------------|
| `app-shell` | Root container | Main app wrapper (sidebar + content) |
| `sidebar` | Aside | Left sidebar panel |
| `sidebar-header` | Div | Sidebar "Menu" header |
| `sidebar-nav` | Nav | Sidebar navigation container |
| `new-chat-btn` | Button | New chat button |
| `session-list` | Div | List of chat sessions |
| `session-item` | Div | Single chat session row (dynamic) |
| `session-item-title` | Span | Session title text |
| `session-item-delete` | Button | Delete chat button on session row |
| `logout-link` | Link | Log out link |
| `sidebar-toggle` | Button | Toggle sidebar (hamburger) |
| `sidebar-overlay` | Div | Overlay when sidebar open (mobile) |
| `chat-header` | Header | Main chat area header |
| `messages` | Section | Scrollable message list |
| `welcome-message` | Article | Initial welcome bot message |
| `message-user` | Div | User message bubble (dynamic) |
| `message-bot` | Div | Bot message bubble (dynamic) |
| `input-bar` | Section | Message input area |
| `file-input` | Input | File upload (hidden) |
| `attach-file-btn` | Label | Attach file button |
| `message-input` | Textarea | Message text input |
| `send-btn` | Button | Send message button |

## Login (`login.html`)

| Test ID | Element | Description |
|---------|---------|-------------|
| `login-layout` | Main | Login page root |
| `login-card` | Div | Login card container |
| `login-header` | Header | "Sign in" title area |
| `login-form` | Form | Login form |
| `form-group-email` | Div | Email field wrapper |
| `login-email` | Input | Email input |
| `form-group-password` | Div | Password field wrapper |
| `login-password` | Input | Password input |
| `login-error` | P | Error message (hidden when empty) |
| `login-submit` | Button | Sign in submit button |

## Example selectors (Playwright / TestSprite)

```js
// Click New chat
await page.click('[data-testid="new-chat-btn"]');

// Type and send message
await page.fill('[data-testid="message-input"]', 'Show salary by department');
await page.click('[data-testid="send-btn"]');

// Login
await page.fill('[data-testid="login-email"]', 'user@example.com');
await page.fill('[data-testid="login-password"]', 'password');
await page.click('[data-testid="login-submit"]');
```
