## Publishing from ChatGPT

Once your GPT Action is connected to chatgpt-wp-bridge, you can use prompts like these.

### Publish normal content
- Publish this as a draft
- Publish this as a page draft
- Publish this as a post draft
- Publish this to WordPress
- Publish this live
- Turn this into a blog post and publish it
- Publish this HTML as a page
- Publish this article with the title "My Title"

### Publish transcripts
- Publish this chat as a draft
- Publish this transcript to WordPress
- Publish this conversation as a page
- Publish this exchange as a post draft

### Control publishing behavior
- Publish this as a post instead of a page
- Publish this live instead of draft
- Use the title "My Custom Title"
- Use a simple slug for this
- Make this private

### Typical defaults
- If you do not specify status, the GPT should use `draft`
- If you do not specify content type, the GPT should use `page`
- If you do not provide a title, the GPT should generate one

### How the GPT decides
- Uses `/publish` for normal HTML/page/post content
- Uses `/publish_transcript` for chats and transcripts
- Returns the resulting WordPress URL after success
