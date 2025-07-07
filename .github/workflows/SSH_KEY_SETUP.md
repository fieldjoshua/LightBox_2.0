# Setting up SSH Keys for GitHub Actions

Since you use SSH key authentication (no passwords), here's how to set it up:

## Step 1: Get your SSH private key

On your local machine (where you SSH from):

```bash
# Your private key is probably in one of these locations:
cat ~/.ssh/id_rsa
# or
cat ~/.ssh/id_ed25519
# or check what key you use:
grep -i "192.168.0.222\|192.168.0.98" ~/.ssh/config
```

## Step 2: Add SSH keys as GitHub secrets

Go to: https://github.com/fieldjoshua/LightBox_2.0/settings/secrets/actions

### For Pi Zero W:
1. Click "New repository secret"
2. Name: `PI_SSH_KEY`
3. Value: Paste your ENTIRE private key (including the BEGIN and END lines)
   ```
   -----BEGIN RSA PRIVATE KEY-----
   (your key content here)
   -----END RSA PRIVATE KEY-----
   ```

### For Pi 3B+:
1. Click "New repository secret"
2. Name: `PI_3B_SSH_KEY`
3. Value: Paste your private key (might be the same key)

## All secrets needed:

### Pi Zero W (10x10 Matrix):
- `PI_HOST` = `192.168.0.222`
- `PI_USER` = `fieldjoshua`
- `PI_SSH_KEY` = (your private SSH key)
- `PI_PORT` = `22`

### Pi 3B+ (HUB75):
- `PI_3B_HOST` = `192.168.0.98`
- `PI_3B_USER` = `joshuafield`
- `PI_3B_SSH_KEY` = (your private SSH key)
- `PI_3B_PORT` = `22`

## Security Note:
- GitHub encrypts these secrets
- They're only accessible to your workflows
- Never commit SSH keys directly to the repository

## Testing:
After adding all secrets, go to Actions tab and manually run one of the workflows to test!