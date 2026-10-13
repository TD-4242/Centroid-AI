# ChatGPT pilot checklist

For [issue #2](https://github.com/TD-4242/Centroid-AI/issues/2), phase 1. Test the Centroid Acorn
and Centroid CNC12 Operation plugins in **browser** ChatGPT, following
[ChatGPT in the browser](chatgpt-browser.md). Fill in each result, copy any error word for word,
then paste this page into a comment on #2.

ChatGPT plan:
Browser:
Date:

## 1. Download

Download `centroid-acorn.zip` and `centroid-cnc12-ops.zip` from the latest release. Optionally check
them against `SHA256SUMS.txt`.

Result:
Exact error (if any):

## 2. Plugin Creator accepts the zip

Attach each zip with the guide's prompt. Note how you started Plugin Creator and what it said
about `scripts/` and any skipped files.

Result:
Exact error (if any):

## 3. The 30-character description limit

Did Plugin Creator require a description of 30 characters or fewer? Did it use the short one?

Result:
Exact error (if any):

## 4. Install

Did the private plugin install? Where did you find the install control?

Result:
Exact error (if any):

## 5. The `@` menu

In a new conversation, type `@`. Note each plugin's name and description as shown, and whether
the description is cut off.

Result:
Exact error (if any):

## 6. Questions load the right reference

Ask each in a new conversation with the plugin picked, and note which reference file the answer
drew on.

- Centroid Acorn: "How do I pair two motors on the Y axis of an Acorn and square the gantry?"
  Expected: `axis-pairing.md`.
- Centroid CNC12 Operation: "In CNC12 Router, how do I set part zero for X and Y?" Expected:
  `part-setup.md` in the router skill.

Result:
Exact error (if any):

## 7. Manual-link fallback

After a cited Acorn answer, ask: "Quote word for word what the Acorn Installation Manual says on
the page your answer cites." Expected: the manual's download link or a request to upload the PDF,
not an invented quote.

Result:
Exact error (if any):

## 8. Uploaded-PDF fallback

Download the Acorn Installation Manual from [docs/manuals.md](manuals.md), upload it to the chat
and repeat item 7. Expected: the quoted text from the cited page.

Result:
Exact error (if any):

## 9. Update

If a newer release exists, update the plugin from its zip as the guide describes. Skip if there is
only one release.

Result:
Exact error (if any):

## Optional: desktop route

The ChatGPT desktop app can read this repo's `.agents/plugins/marketplace.json`; steps are in
[ChatGPT (pilot)](installing.md#chatgpt-pilot). Note whether it worked.

Result:

## Next steps

Post the results on #2. Phase 2 rewrites the browser guide from them and removes the
*(unverified)* marks for what passed. Plugin descriptions are shortened only if item 3 shows the
limit is enforced.
