# CHANGELOG


## v0.1.0 (2025-08-09)

### Bug Fixes

- Add section project scripts
  ([`d34ce3e`](https://github.com/myriade-ai/autocode/commit/d34ce3e7f0275657ea556471bc3bf2403e06ed9d))

- Cli loop
  ([`201bfa8`](https://github.com/myriade-ai/autocode/commit/201bfa8888224597c14e1e72fabcc0b92dbdee12))

- Code
  ([`84d9fef`](https://github.com/myriade-ai/autocode/commit/84d9fef858ea9d08bd84e0defd5cadd9dfe4d907))

- Cut to 1000 lines
  ([`31ad216`](https://github.com/myriade-ai/autocode/commit/31ad216ffad36712f4d5c5cc14a81562a503fcfa))

- Follow parent .gitignore files
  ([`02491a1`](https://github.com/myriade-ai/autocode/commit/02491a13e54cfa8284972f9511c0a3d415ddd86e))

### Build System

- Add semantic release
  ([`5901545`](https://github.com/myriade-ai/autocode/commit/59015459b0a7f52022c02d8ef40292ecb151e47b))

### Chores

- Add open files concept
  ([`170c3f9`](https://github.com/myriade-ai/autocode/commit/170c3f91d996e6e815ffc3f17f0a2e087e985144))

PRO-167

- Change
  ([`5c473ba`](https://github.com/myriade-ai/autocode/commit/5c473baa723e0eab8645dbb009870340d38ee308))

- Draft for git & pr
  ([`ea42f4d`](https://github.com/myriade-ai/autocode/commit/ea42f4dda377420c7e69d093b485d350654eab55))

- Fix AUTOCHAT_OUTPUT_SIZE_LIMIT for read_file, add warning on text long
  ([`05a6622`](https://github.com/myriade-ai/autocode/commit/05a6622c5b7560d1d05ab58cf475e62b2fb06d73))

- Fix typing for 3.9
  ([`1108205`](https://github.com/myriade-ai/autocode/commit/11082054826792cc89e1fb21a65e4a5592cfbbdc))

- Improve edit functions
  ([`44f7014`](https://github.com/myriade-ai/autocode/commit/44f7014409a905d97364b3d5233d09bacdc30e59))

- Improve instruction
  ([`03cbe15`](https://github.com/myriade-ai/autocode/commit/03cbe152f27644bfbffc4250b6144cc2dc3d34dd))

- Remove file from cli for readability
  ([`5e059da`](https://github.com/myriade-ai/autocode/commit/5e059daa12f86a4fe90bb997edde79423e5535e7))

- Switch to logger instead of print
  ([`9bfd081`](https://github.com/myriade-ai/autocode/commit/9bfd0816e4e093350356a960a997469f3c5398cb))

- Try to clean instruction
  ([`39faff3`](https://github.com/myriade-ai/autocode/commit/39faff3f0876844acaa69ffff236bba6bd475a33))

### Documentation

- Enhance README with detailed CLI usage instructions
  ([`7898a5a`](https://github.com/myriade-ai/autocode/commit/7898a5a59540d5a807ac27e09635d963978e3c64))

- Update README
  ([`bac8cc8`](https://github.com/myriade-ai/autocode/commit/bac8cc8bf9a099748cc3106c7bb27b9a0b11319f))

### Features

- Add autocode exports and misc
  ([`38aa4c5`](https://github.com/myriade-ai/autocode/commit/38aa4c5ac1ac5b71334691e8b489d5bfc8865949))

- Add bootstrap mecanism
  ([`2bad51d`](https://github.com/myriade-ai/autocode/commit/2bad51d2c057a336d04aa88f04f23f9515ae48f2))

- Add build pipeline
  ([`389062b`](https://github.com/myriade-ai/autocode/commit/389062b12ef9923d91ddcdecf547b8d26e55496b))

- Update code & docs
  ([`cafeba5`](https://github.com/myriade-ai/autocode/commit/cafeba541bbba7892ac9dff9483cdad06114cb12))

- **server**: Add micro HTTP server to listen for GitHub issue webhooks
  ([`ba5362d`](https://github.com/myriade-ai/autocode/commit/ba5362d28065d6a1c7cdfcbfe16f5036b06dc6cb))

The new `autocode.github_issue_server` module provides a tiny HTTP server able to receive GitHub
  "issues" webhooks. When a new issue is opened, the issue title and body are concatenated into a
  prompt and fed to the developer agent in a background thread.

A console entry point `autocode-github-issue-server` has been added to `pyproject.toml` so the
  server can be started with a simple CLI command.
