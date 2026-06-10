"""
tools_productivity.py — Productivity Tools for NPM Agent (NPMAI ECOSYSTEM)
Author: Sonu Kumar / NPMAI ECOSYSTEM
Tools: GoogleWorkspace, NotionAdvanced, Linear, Asana, Trello, ClickUp,
       Todoist, Obsidian, BookmarkManager, TimeTracking
"""

import os, sys, json, re, csv, time, sqlite3, subprocess, tempfile, traceback
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Optional, Any

# ── auto-install helpers ──────────────────────────────────────────────────────
def _ensure(pkg: str, import_name: str = None):
    n = import_name or pkg
    try:
        __import__(n)
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg, "-q"],
                       check=False)

for _pkg, _imp in [
    ("google-api-python-client", "googleapiclient"),
    ("google-auth-httplib2",     "google_auth_httplib2"),
    ("google-auth-oauthlib",     "google_auth_oauthlib"),
    ("google-auth",              "google.oauth2"),
    ("notion-client",            "notion_client"),
    ("requests",                 "requests"),
    ("asana",                    "asana"),
    ("todoist-api-python",       "todoist_api_python"),
    ("python-frontmatter",       "frontmatter"),
    ("beautifulsoup4",           "bs4"),
    ("playwright",               "playwright"),
    ("cryptography",             "cryptography"),
]:
    _ensure(_pkg, _imp)

from agent_core import ToolResult, CredStore

# ═════════════════════════════════════════════════════════════════════════════
# 1. GoogleWorkspaceTool
# ═════════════════════════════════════════════════════════════════════════════

class GoogleWorkspaceTool:
    name = "google_workspace"
    description = (
        "Google Docs, Sheets, Drive, and Forms — create, read, write, "
        "share, export, upload, download, and manage files"
    )

    # ── internal helpers ──────────────────────────────────────────────────

    @staticmethod
    def _creds(cred_key: str = "google"):
        """Return google.oauth2 Credentials from stored service-account JSON."""
        from google.oauth2.service_account import Credentials
        data = CredStore.load(cred_key)
        if not data:
            raise ValueError("No Google credentials. Store service-account JSON under 'google'.")
        scopes = [
            "https://www.googleapis.com/auth/documents",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/forms",
        ]
        return Credentials.from_service_account_info(data, scopes=scopes)

    @staticmethod
    def _docs_service(cred_key: str = "google"):
        from googleapiclient.discovery import build
        return build("docs", "v1", credentials=GoogleWorkspaceTool._creds(cred_key))

    @staticmethod
    def _sheets_service(cred_key: str = "google"):
        from googleapiclient.discovery import build
        return build("sheets", "v4", credentials=GoogleWorkspaceTool._creds(cred_key))

    @staticmethod
    def _drive_service(cred_key: str = "google"):
        from googleapiclient.discovery import build
        return build("drive", "v3", credentials=GoogleWorkspaceTool._creds(cred_key))

    @staticmethod
    def _forms_service(cred_key: str = "google"):
        from googleapiclient.discovery import build
        return build("forms", "v1", credentials=GoogleWorkspaceTool._creds(cred_key))

    # ── Docs ─────────────────────────────────────────────────────────────

    @staticmethod
    def docs_create(title: str, content: str, cred_key: str = "google") -> ToolResult:
        try:
            svc = GoogleWorkspaceTool._docs_service(cred_key)
            doc = svc.documents().create(body={"title": title}).execute()
            doc_id = doc["documentId"]
            if content:
                requests_ = [{"insertText": {"location": {"index": 1}, "text": content}}]
                svc.documents().batchUpdate(documentId=doc_id,
                                            body={"requests": requests_}).execute()
            return ToolResult(True, f"✓ Doc created: {doc_id}",
                              {"documentId": doc_id, "title": title})
        except Exception as e:
            return ToolResult(False, f"✗ docs_create failed: {e}")

    @staticmethod
    def docs_get(doc_id: str, cred_key: str = "google") -> ToolResult:
        try:
            svc = GoogleWorkspaceTool._docs_service(cred_key)
            doc = svc.documents().get(documentId=doc_id).execute()
            # extract plain text
            text_parts = []
            for el in doc.get("body", {}).get("content", []):
                for run in el.get("paragraph", {}).get("elements", []):
                    t = run.get("textRun", {}).get("content", "")
                    if t:
                        text_parts.append(t)
            plain = "".join(text_parts)
            return ToolResult(True, f"✓ Doc fetched ({len(plain)} chars)",
                              {"doc": doc, "plain_text": plain})
        except Exception as e:
            return ToolResult(False, f"✗ docs_get failed: {e}")

    @staticmethod
    def docs_append(doc_id: str, content: str, cred_key: str = "google") -> ToolResult:
        try:
            svc = GoogleWorkspaceTool._docs_service(cred_key)
            doc = svc.documents().get(documentId=doc_id).execute()
            end_index = doc["body"]["content"][-1]["endIndex"] - 1
            requests_ = [{"insertText": {"location": {"index": end_index}, "text": content}}]
            svc.documents().batchUpdate(documentId=doc_id,
                                        body={"requests": requests_}).execute()
            return ToolResult(True, f"✓ Appended {len(content)} chars to {doc_id}")
        except Exception as e:
            return ToolResult(False, f"✗ docs_append failed: {e}")

    @staticmethod
    def docs_replace_text(doc_id: str, replacements: dict,
                          cred_key: str = "google") -> ToolResult:
        """replacements: {old_text: new_text, ...}"""
        try:
            svc = GoogleWorkspaceTool._docs_service(cred_key)
            requests_ = [
                {"replaceAllText": {
                    "containsText": {"text": old, "matchCase": True},
                    "replaceText": new
                }}
                for old, new in replacements.items()
            ]
            result = svc.documents().batchUpdate(documentId=doc_id,
                                                  body={"requests": requests_}).execute()
            return ToolResult(True, f"✓ Replaced {len(replacements)} text(s)", result)
        except Exception as e:
            return ToolResult(False, f"✗ docs_replace_text failed: {e}")

    @staticmethod
    def docs_export(doc_id: str, format: str = "pdf",
                    output: str = "document.pdf", cred_key: str = "google") -> ToolResult:
        """format: pdf | docx | txt | html | odt"""
        try:
            mime_map = {
                "pdf":  "application/pdf",
                "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "txt":  "text/plain",
                "html": "text/html",
                "odt":  "application/vnd.oasis.opendocument.text",
            }
            mime = mime_map.get(format.lower(), "application/pdf")
            svc = GoogleWorkspaceTool._drive_service(cred_key)
            content_bytes = svc.files().export_media(fileId=doc_id,
                                                      mimeType=mime).execute()
            Path(output).write_bytes(content_bytes)
            return ToolResult(True, f"✓ Exported to {output}")
        except Exception as e:
            return ToolResult(False, f"✗ docs_export failed: {e}")

    # ── Sheets ────────────────────────────────────────────────────────────

    @staticmethod
    def sheets_create(title: str, sheets: list = None,
                      cred_key: str = "google") -> ToolResult:
        """sheets: list of sheet names, e.g. ['Sheet1','Data']"""
        try:
            svc = GoogleWorkspaceTool._sheets_service(cred_key)
            body = {"properties": {"title": title}}
            if sheets:
                body["sheets"] = [{"properties": {"title": s}} for s in sheets]
            ss = svc.spreadsheets().create(body=body).execute()
            return ToolResult(True, f"✓ Spreadsheet created: {ss['spreadsheetId']}",
                              {"spreadsheetId": ss["spreadsheetId"],
                               "url": ss["spreadsheetUrl"]})
        except Exception as e:
            return ToolResult(False, f"✗ sheets_create failed: {e}")

    @staticmethod
    def sheets_read(spreadsheet_id: str, range_: str = "Sheet1",
                    cred_key: str = "google") -> ToolResult:
        try:
            svc = GoogleWorkspaceTool._sheets_service(cred_key)
            resp = svc.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=range_).execute()
            values = resp.get("values", [])
            return ToolResult(True, f"✓ Read {len(values)} rows", values)
        except Exception as e:
            return ToolResult(False, f"✗ sheets_read failed: {e}")

    @staticmethod
    def sheets_write(spreadsheet_id: str, range_: str,
                     values: list, value_input_option: str = "RAW",
                     cred_key: str = "google") -> ToolResult:
        try:
            svc = GoogleWorkspaceTool._sheets_service(cred_key)
            body = {"values": values}
            resp = svc.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, range=range_,
                valueInputOption=value_input_option, body=body).execute()
            return ToolResult(True, f"✓ Written {resp.get('updatedCells',0)} cells")
        except Exception as e:
            return ToolResult(False, f"✗ sheets_write failed: {e}")

    @staticmethod
    def sheets_append(spreadsheet_id: str, range_: str, values: list,
                      cred_key: str = "google") -> ToolResult:
        try:
            svc = GoogleWorkspaceTool._sheets_service(cred_key)
            body = {"values": values}
            resp = svc.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id, range=range_,
                valueInputOption="RAW", insertDataOption="INSERT_ROWS",
                body=body).execute()
            return ToolResult(True, f"✓ Appended rows",
                              resp.get("updates", {}))
        except Exception as e:
            return ToolResult(False, f"✗ sheets_append failed: {e}")

    @staticmethod
    def sheets_clear(spreadsheet_id: str, range_: str,
                     cred_key: str = "google") -> ToolResult:
        try:
            svc = GoogleWorkspaceTool._sheets_service(cred_key)
            svc.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id, range=range_, body={}).execute()
            return ToolResult(True, f"✓ Cleared {range_}")
        except Exception as e:
            return ToolResult(False, f"✗ sheets_clear failed: {e}")

    @staticmethod
    def sheets_format_cells(spreadsheet_id: str, range_: str,
                            format: dict, cred_key: str = "google") -> ToolResult:
        """format: CellFormat dict e.g. {'backgroundColor': {'red':1,'green':0,'blue':0}}"""
        try:
            svc = GoogleWorkspaceTool._sheets_service(cred_key)
            # Parse range to get sheet id
            meta = svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheet_id = meta["sheets"][0]["properties"]["sheetId"]
            requests_ = [{
                "repeatCell": {
                    "range": {"sheetId": sheet_id},
                    "cell": {"userEnteredFormat": format},
                    "fields": "userEnteredFormat"
                }
            }]
            svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                           body={"requests": requests_}).execute()
            return ToolResult(True, f"✓ Format applied to {range_}")
        except Exception as e:
            return ToolResult(False, f"✗ sheets_format_cells failed: {e}")

    @staticmethod
    def sheets_add_chart(spreadsheet_id: str, sheet_id: int,
                         chart_config: dict, cred_key: str = "google") -> ToolResult:
        """chart_config: AddChartRequest spec dict from Sheets API"""
        try:
            svc = GoogleWorkspaceTool._sheets_service(cred_key)
            requests_ = [{"addChart": {"chart": chart_config}}]
            resp = svc.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": requests_}).execute()
            return ToolResult(True, "✓ Chart added", resp)
        except Exception as e:
            return ToolResult(False, f"✗ sheets_add_chart failed: {e}")

    # ── Drive ─────────────────────────────────────────────────────────────

    @staticmethod
    def drive_upload(local_path: str, folder_id: str = None,
                     mime_type: str = None, cred_key: str = "google") -> ToolResult:
        try:
            from googleapiclient.http import MediaFileUpload
            svc = GoogleWorkspaceTool._drive_service(cred_key)
            name = Path(local_path).name
            meta = {"name": name}
            if folder_id:
                meta["parents"] = [folder_id]
            media = MediaFileUpload(local_path, mimetype=mime_type,
                                    resumable=True)
            f = svc.files().create(body=meta, media_body=media,
                                   fields="id,name,webViewLink").execute()
            return ToolResult(True, f"✓ Uploaded {name}", f)
        except Exception as e:
            return ToolResult(False, f"✗ drive_upload failed: {e}")

    @staticmethod
    def drive_download(file_id: str, output_path: str,
                       cred_key: str = "google") -> ToolResult:
        try:
            import io
            from googleapiclient.http import MediaIoBaseDownload
            svc = GoogleWorkspaceTool._drive_service(cred_key)
            request = svc.files().get_media(fileId=file_id)
            buf = io.BytesIO()
            dl = MediaIoBaseDownload(buf, request)
            done = False
            while not done:
                _, done = dl.next_chunk()
            Path(output_path).write_bytes(buf.getvalue())
            return ToolResult(True, f"✓ Downloaded to {output_path}")
        except Exception as e:
            return ToolResult(False, f"✗ drive_download failed: {e}")

    @staticmethod
    def drive_list(folder_id: str = None, query: str = None,
                   order_by: str = "name", cred_key: str = "google") -> ToolResult:
        try:
            svc = GoogleWorkspaceTool._drive_service(cred_key)
            q_parts = []
            if folder_id:
                q_parts.append(f"'{folder_id}' in parents")
            if query:
                q_parts.append(query)
            q_parts.append("trashed=false")
            q_str = " and ".join(q_parts)
            results = svc.files().list(
                q=q_str, orderBy=order_by,
                fields="files(id,name,mimeType,size,modifiedTime,webViewLink)"
            ).execute()
            files = results.get("files", [])
            return ToolResult(True, f"✓ {len(files)} files", files)
        except Exception as e:
            return ToolResult(False, f"✗ drive_list failed: {e}")

    @staticmethod
    def drive_create_folder(name: str, parent_id: str = None,
                            cred_key: str = "google") -> ToolResult:
        try:
            svc = GoogleWorkspaceTool._drive_service(cred_key)
            meta = {"name": name,
                    "mimeType": "application/vnd.google-apps.folder"}
            if parent_id:
                meta["parents"] = [parent_id]
            folder = svc.files().create(body=meta,
                                        fields="id,name").execute()
            return ToolResult(True, f"✓ Folder created: {folder['id']}", folder)
        except Exception as e:
            return ToolResult(False, f"✗ drive_create_folder failed: {e}")

    @staticmethod
    def drive_share(file_id: str, email: str, role: str = "reader",
                    cred_key: str = "google") -> ToolResult:
        """role: reader | writer | commenter | owner"""
        try:
            svc = GoogleWorkspaceTool._drive_service(cred_key)
            perm = {"type": "user", "role": role, "emailAddress": email}
            resp = svc.permissions().create(fileId=file_id, body=perm,
                                            sendNotificationEmail=True).execute()
            return ToolResult(True, f"✓ Shared {file_id} with {email} as {role}", resp)
        except Exception as e:
            return ToolResult(False, f"✗ drive_share failed: {e}")

    @staticmethod
    def drive_move(file_id: str, new_parent_id: str,
                   cred_key: str = "google") -> ToolResult:
        try:
            svc = GoogleWorkspaceTool._drive_service(cred_key)
            f = svc.files().get(fileId=file_id, fields="parents").execute()
            old_parents = ",".join(f.get("parents", []))
            svc.files().update(fileId=file_id,
                               addParents=new_parent_id,
                               removeParents=old_parents,
                               fields="id,parents").execute()
            return ToolResult(True, f"✓ Moved {file_id} to {new_parent_id}")
        except Exception as e:
            return ToolResult(False, f"✗ drive_move failed: {e}")

    # ── Forms ─────────────────────────────────────────────────────────────

    @staticmethod
    def forms_create(title: str, items: list,
                     cred_key: str = "google") -> ToolResult:
        """
        items: list of dicts, e.g.
          [{"title": "Name?", "type": "TEXT"},
           {"title": "Age?",  "type": "TEXT"},
           {"title": "Color?","type":"RADIO","options":["Red","Blue"]}]
        """
        try:
            svc = GoogleWorkspaceTool._forms_service(cred_key)
            form = svc.forms().create(
                body={"info": {"title": title, "documentTitle": title}}
            ).execute()
            form_id = form["formId"]
            requests_ = []
            for idx, item in enumerate(items):
                q_type = item.get("type", "TEXT").upper()
                question: dict = {}
                if q_type == "TEXT":
                    question = {"textQuestion": {"paragraph": False}}
                elif q_type == "RADIO":
                    opts = [{"value": o} for o in item.get("options", [])]
                    question = {"choiceQuestion": {"type": "RADIO",
                                                   "options": opts}}
                elif q_type == "CHECKBOX":
                    opts = [{"value": o} for o in item.get("options", [])]
                    question = {"choiceQuestion": {"type": "CHECKBOX",
                                                   "options": opts}}
                elif q_type == "SCALE":
                    question = {"scaleQuestion": {"low": 1, "high": 5}}
                requests_.append({
                    "createItem": {
                        "item": {
                            "title": item.get("title", f"Question {idx+1}"),
                            "questionItem": {"question": question}
                        },
                        "location": {"index": idx}
                    }
                })
            if requests_:
                svc.forms().batchUpdate(formId=form_id,
                                        body={"requests": requests_}).execute()
            return ToolResult(True, f"✓ Form created: {form_id}",
                              {"formId": form_id,
                               "responderUri": form.get("responderUri", "")})
        except Exception as e:
            return ToolResult(False, f"✗ forms_create failed: {e}")

    @staticmethod
    def forms_get_responses(form_id: str,
                            cred_key: str = "google") -> ToolResult:
        try:
            svc = GoogleWorkspaceTool._forms_service(cred_key)
            resp = svc.forms().responses().list(formId=form_id).execute()
            responses = resp.get("responses", [])
            return ToolResult(True, f"✓ {len(responses)} responses", responses)
        except Exception as e:
            return ToolResult(False, f"✗ forms_get_responses failed: {e}")

    @staticmethod
    def forms_list(cred_key: str = "google") -> ToolResult:
        try:
            svc = GoogleWorkspaceTool._drive_service(cred_key)
            results = svc.files().list(
                q="mimeType='application/vnd.google-apps.form' and trashed=false",
                fields="files(id,name,modifiedTime,webViewLink)"
            ).execute()
            forms = results.get("files", [])
            return ToolResult(True, f"✓ {len(forms)} forms", forms)
        except Exception as e:
            return ToolResult(False, f"✗ forms_list failed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 2. NotionAdvancedTool
# ═════════════════════════════════════════════════════════════════════════════

class NotionAdvancedTool:
    name = "notion_advanced"
    description = (
        "Advanced Notion operations — databases, pages, blocks, tables, "
        "kanban views, CSV import/export, templates, and page duplication"
    )

    @staticmethod
    def _client(cred_key: str = "notion"):
        from notion_client import Client
        token = CredStore.load(cred_key).get("token", "")
        if not token:
            raise ValueError("No Notion token. Store under 'notion' key.")
        return Client(auth=token)

    @staticmethod
    def _rich_text(s: str) -> list:
        return [{"type": "text", "text": {"content": s}}]

    # ── Search / Database ────────────────────────────────────────────────

    @staticmethod
    def search(query: str, filter_type: str = None,
               sort: str = "last_edited_time",
               cred_key: str = "notion") -> ToolResult:
        try:
            n = NotionAdvancedTool._client(cred_key)
            body: dict = {"query": query,
                          "sort": {"direction": "descending",
                                   "timestamp": sort}}
            if filter_type:
                body["filter"] = {"value": filter_type, "property": "object"}
            resp = n.search(**body)
            results = resp.get("results", [])
            return ToolResult(True, f"✓ {len(results)} results", results)
        except Exception as e:
            return ToolResult(False, f"✗ search failed: {e}")

    @staticmethod
    def get_database(database_id: str,
                     cred_key: str = "notion") -> ToolResult:
        try:
            n = NotionAdvancedTool._client(cred_key)
            db = n.databases.retrieve(database_id=database_id)
            return ToolResult(True, "✓ Database retrieved", db)
        except Exception as e:
            return ToolResult(False, f"✗ get_database failed: {e}")

    @staticmethod
    def query_database(database_id: str, filter: dict = None,
                       sorts: list = None, page_size: int = 100,
                       cred_key: str = "notion") -> ToolResult:
        try:
            n = NotionAdvancedTool._client(cred_key)
            kwargs: dict = {"database_id": database_id,
                            "page_size": page_size}
            if filter:
                kwargs["filter"] = filter
            if sorts:
                kwargs["sorts"] = sorts
            resp = n.databases.query(**kwargs)
            rows = resp.get("results", [])
            return ToolResult(True, f"✓ {len(rows)} rows", rows)
        except Exception as e:
            return ToolResult(False, f"✗ query_database failed: {e}")

    @staticmethod
    def create_database(parent_id: str, title: str, properties: dict,
                        cred_key: str = "notion") -> ToolResult:
        """
        properties: Notion property schema dict, e.g.
          {"Name": {"title": {}}, "Status": {"select": {}}}
        """
        try:
            n = NotionAdvancedTool._client(cred_key)
            db = n.databases.create(
                parent={"type": "page_id", "page_id": parent_id},
                title=NotionAdvancedTool._rich_text(title),
                properties=properties
            )
            return ToolResult(True, f"✓ Database created: {db['id']}", db)
        except Exception as e:
            return ToolResult(False, f"✗ create_database failed: {e}")

    @staticmethod
    def add_database_item(database_id: str, properties: dict,
                          cred_key: str = "notion") -> ToolResult:
        try:
            n = NotionAdvancedTool._client(cred_key)
            page = n.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            return ToolResult(True, f"✓ Item added: {page['id']}", page)
        except Exception as e:
            return ToolResult(False, f"✗ add_database_item failed: {e}")

    @staticmethod
    def update_database_item(page_id: str, properties: dict,
                              cred_key: str = "notion") -> ToolResult:
        try:
            n = NotionAdvancedTool._client(cred_key)
            page = n.pages.update(page_id=page_id, properties=properties)
            return ToolResult(True, f"✓ Item updated: {page_id}", page)
        except Exception as e:
            return ToolResult(False, f"✗ update_database_item failed: {e}")

    @staticmethod
    def delete_database_item(page_id: str,
                             cred_key: str = "notion") -> ToolResult:
        try:
            n = NotionAdvancedTool._client(cred_key)
            n.pages.update(page_id=page_id, archived=True)
            return ToolResult(True, f"✓ Item archived/deleted: {page_id}")
        except Exception as e:
            return ToolResult(False, f"✗ delete_database_item failed: {e}")

    # ── Pages ─────────────────────────────────────────────────────────────

    @staticmethod
    def create_page(parent_id: str, title: str,
                    content_blocks: list = None,
                    cred_key: str = "notion") -> ToolResult:
        """
        content_blocks: list of Notion block dicts.
        If None, a simple paragraph is created.
        """
        try:
            n = NotionAdvancedTool._client(cred_key)
            children = content_blocks or [{
                "object": "block", "type": "paragraph",
                "paragraph": {"rich_text": NotionAdvancedTool._rich_text("")}
            }]
            page = n.pages.create(
                parent={"page_id": parent_id},
                properties={"title": {"title": NotionAdvancedTool._rich_text(title)}},
                children=children
            )
            return ToolResult(True, f"✓ Page created: {page['url']}", page)
        except Exception as e:
            return ToolResult(False, f"✗ create_page failed: {e}")

    @staticmethod
    def get_page(page_id: str, cred_key: str = "notion") -> ToolResult:
        try:
            n = NotionAdvancedTool._client(cred_key)
            page = n.pages.retrieve(page_id=page_id)
            return ToolResult(True, "✓ Page retrieved", page)
        except Exception as e:
            return ToolResult(False, f"✗ get_page failed: {e}")

    @staticmethod
    def update_page(page_id: str, properties: dict,
                    cred_key: str = "notion") -> ToolResult:
        try:
            n = NotionAdvancedTool._client(cred_key)
            page = n.pages.update(page_id=page_id, properties=properties)
            return ToolResult(True, f"✓ Page updated: {page_id}", page)
        except Exception as e:
            return ToolResult(False, f"✗ update_page failed: {e}")

    # ── Blocks ────────────────────────────────────────────────────────────

    @staticmethod
    def append_blocks(block_id: str, children: list,
                      cred_key: str = "notion") -> ToolResult:
        try:
            n = NotionAdvancedTool._client(cred_key)
            resp = n.blocks.children.append(block_id=block_id,
                                            children=children)
            return ToolResult(True, f"✓ Blocks appended", resp)
        except Exception as e:
            return ToolResult(False, f"✗ append_blocks failed: {e}")

    @staticmethod
    def get_blocks(block_id: str, cred_key: str = "notion") -> ToolResult:
        try:
            n = NotionAdvancedTool._client(cred_key)
            resp = n.blocks.children.list(block_id=block_id)
            return ToolResult(True, f"✓ {len(resp.get('results',[]))} blocks",
                              resp.get("results", []))
        except Exception as e:
            return ToolResult(False, f"✗ get_blocks failed: {e}")

    @staticmethod
    def delete_block(block_id: str, cred_key: str = "notion") -> ToolResult:
        try:
            n = NotionAdvancedTool._client(cred_key)
            n.blocks.delete(block_id=block_id)
            return ToolResult(True, f"✓ Block deleted: {block_id}")
        except Exception as e:
            return ToolResult(False, f"✗ delete_block failed: {e}")

    # ── Special structures ────────────────────────────────────────────────

    @staticmethod
    def create_table(parent_id: str, headers: list, rows: list,
                     cred_key: str = "notion") -> ToolResult:
        """headers: ['Col1','Col2'...], rows: [['v1','v2'...], ...]"""
        try:
            n = NotionAdvancedTool._client(cred_key)
            table_width = len(headers)

            def _cell(text: str) -> list:
                return [{"type": "text", "text": {"content": text}}]

            table_rows = []
            # header row
            table_rows.append({
                "type": "table_row", "object": "block",
                "table_row": {"cells": [_cell(h) for h in headers]}
            })
            # data rows
            for row in rows:
                cells = [_cell(str(v)) for v in row]
                while len(cells) < table_width:
                    cells.append(_cell(""))
                table_rows.append({
                    "type": "table_row", "object": "block",
                    "table_row": {"cells": cells[:table_width]}
                })
            block = {
                "object": "block", "type": "table",
                "table": {
                    "table_width": table_width,
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": table_rows
                }
            }
            resp = n.blocks.children.append(block_id=parent_id,
                                            children=[block])
            return ToolResult(True, f"✓ Table created with {len(rows)} rows", resp)
        except Exception as e:
            return ToolResult(False, f"✗ create_table failed: {e}")

    @staticmethod
    def create_kanban_view(database_id: str,
                           cred_key: str = "notion") -> ToolResult:
        """Adds a 'Status' select property and board view to the database."""
        try:
            n = NotionAdvancedTool._client(cred_key)
            # Ensure Status property exists
            n.databases.update(
                database_id=database_id,
                properties={
                    "Status": {
                        "select": {
                            "options": [
                                {"name": "Todo",        "color": "gray"},
                                {"name": "In Progress", "color": "blue"},
                                {"name": "Done",        "color": "green"},
                            ]
                        }
                    }
                }
            )
            return ToolResult(True, "✓ Kanban Status property added to database")
        except Exception as e:
            return ToolResult(False, f"✗ create_kanban_view failed: {e}")

    @staticmethod
    def export_database_to_csv(database_id: str, output: str,
                               cred_key: str = "notion") -> ToolResult:
        try:
            n = NotionAdvancedTool._client(cred_key)
            rows = []
            cursor = None
            while True:
                kwargs: dict = {"database_id": database_id, "page_size": 100}
                if cursor:
                    kwargs["start_cursor"] = cursor
                resp = n.databases.query(**kwargs)
                rows.extend(resp.get("results", []))
                if not resp.get("has_more"):
                    break
                cursor = resp.get("next_cursor")

            if not rows:
                return ToolResult(True, "✓ No rows to export", [])

            # Flatten properties
            all_keys: set = set()
            flat_rows = []
            for row in rows:
                flat: dict = {"id": row["id"]}
                for prop_name, prop_val in row.get("properties", {}).items():
                    ptype = prop_val.get("type", "")
                    if ptype == "title":
                        val = "".join(t["text"]["content"]
                                      for t in prop_val.get("title", []))
                    elif ptype == "rich_text":
                        val = "".join(t["text"]["content"]
                                      for t in prop_val.get("rich_text", []))
                    elif ptype == "select":
                        val = (prop_val.get("select") or {}).get("name", "")
                    elif ptype == "multi_select":
                        val = ", ".join(o["name"] for o in prop_val.get("multi_select", []))
                    elif ptype == "checkbox":
                        val = str(prop_val.get("checkbox", False))
                    elif ptype == "number":
                        val = str(prop_val.get("number", ""))
                    elif ptype == "date":
                        d = prop_val.get("date") or {}
                        val = d.get("start", "")
                    elif ptype == "url":
                        val = prop_val.get("url", "") or ""
                    elif ptype == "email":
                        val = prop_val.get("email", "") or ""
                    elif ptype == "phone_number":
                        val = prop_val.get("phone_number", "") or ""
                    else:
                        val = str(prop_val)
                    flat[prop_name] = val
                    all_keys.add(prop_name)
                flat_rows.append(flat)

            cols = ["id"] + sorted(all_keys)
            with open(output, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
                w.writeheader()
                w.writerows(flat_rows)
            return ToolResult(True, f"✓ Exported {len(flat_rows)} rows to {output}")
        except Exception as e:
            return ToolResult(False, f"✗ export_database_to_csv failed: {e}")

    @staticmethod
    def import_csv_to_database(database_id: str, csv_path: str,
                                property_mapping: dict = None,
                                cred_key: str = "notion") -> ToolResult:
        """
        property_mapping: {csv_col: notion_property_name} — defaults to identity.
        All values imported as rich_text unless column name is 'title'/'Title'.
        """
        try:
            n = NotionAdvancedTool._client(cred_key)
            mapping = property_mapping or {}
            added = 0
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    props: dict = {}
                    for col, val in row.items():
                        notion_col = mapping.get(col, col)
                        if notion_col.lower() == "title":
                            props[notion_col] = {
                                "title": [{"text": {"content": val or ""}}]}
                        else:
                            props[notion_col] = {
                                "rich_text": [{"text": {"content": val or ""}}]}
                    n.pages.create(
                        parent={"database_id": database_id},
                        properties=props
                    )
                    added += 1
            return ToolResult(True, f"✓ Imported {added} rows")
        except Exception as e:
            return ToolResult(False, f"✗ import_csv_to_database failed: {e}")

    @staticmethod
    def create_template(parent_id: str, template_data: dict,
                        cred_key: str = "notion") -> ToolResult:
        """
        template_data: {title, content_blocks, icon, cover}
        Creates a page intended as a reusable template.
        """
        try:
            n = NotionAdvancedTool._client(cred_key)
            body: dict = {
                "parent": {"page_id": parent_id},
                "properties": {
                    "title": {
                        "title": NotionAdvancedTool._rich_text(
                            template_data.get("title", "Template"))
                    }
                },
            }
            if template_data.get("icon"):
                body["icon"] = {"type": "emoji",
                                "emoji": template_data["icon"]}
            if template_data.get("cover"):
                body["cover"] = {"type": "external",
                                 "external": {"url": template_data["cover"]}}
            if template_data.get("content_blocks"):
                body["children"] = template_data["content_blocks"]
            page = n.pages.create(**body)
            return ToolResult(True, f"✓ Template created: {page['url']}", page)
        except Exception as e:
            return ToolResult(False, f"✗ create_template failed: {e}")

    @staticmethod
    def duplicate_page(page_id: str, parent_id: str,
                       cred_key: str = "notion") -> ToolResult:
        try:
            n = NotionAdvancedTool._client(cred_key)
            orig = n.pages.retrieve(page_id=page_id)
            blocks_resp = n.blocks.children.list(block_id=page_id)
            children = blocks_resp.get("results", [])
            # strip server-managed fields from blocks
            clean_children = []
            skip_keys = {"id", "created_time", "last_edited_time",
                         "created_by", "last_edited_by", "has_children"}
            for b in children:
                cb = {k: v for k, v in b.items() if k not in skip_keys}
                clean_children.append(cb)
            new_page = n.pages.create(
                parent={"page_id": parent_id},
                properties=orig.get("properties", {}),
                children=clean_children[:100]  # API limit
            )
            return ToolResult(True, f"✓ Page duplicated: {new_page['url']}", new_page)
        except Exception as e:
            return ToolResult(False, f"✗ duplicate_page failed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 3. LinearTool
# ═════════════════════════════════════════════════════════════════════════════

class LinearTool:
    name = "linear"
    description = (
        "Linear project management — issues, teams, projects, labels, "
        "cycles, members, and comments via GraphQL API"
    )

    @staticmethod
    def _gql(query: str, variables: dict = None,
             cred_key: str = "linear") -> dict:
        import requests
        token = CredStore.load(cred_key).get("api_key", "")
        if not token:
            raise ValueError("No Linear API key. Store under 'linear' key.")
        resp = requests.post(
            "https://api.linear.app/graphql",
            json={"query": query, "variables": variables or {}},
            headers={"Authorization": token,
                     "Content-Type": "application/json"},
            timeout=20
        )
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise ValueError(data["errors"][0].get("message", "GraphQL error"))
        return data.get("data", {})

    # ── Issues ────────────────────────────────────────────────────────────

    @staticmethod
    def list_issues(team_id: str = None, state: str = None,
                    assignee: str = None, priority: int = None,
                    label: str = None,
                    cred_key: str = "linear") -> ToolResult:
        try:
            filters = []
            if team_id:
                filters.append(f'team: {{id: {{eq: "{team_id}"}}}}')
            if state:
                filters.append(f'state: {{name: {{eq: "{state}"}}}}')
            if assignee:
                filters.append(f'assignee: {{id: {{eq: "{assignee}"}}}}')
            if priority is not None:
                filters.append(f"priority: {{eq: {priority}}}")
            filter_str = ("{" + ", ".join(filters) + "}") if filters else ""
            filter_arg = f"(filter: {filter_str})" if filter_str else "(first: 50)"
            q = f"""
            query {{
              issues{filter_arg} {{
                nodes {{
                  id title state {{ name }} priority
                  assignee {{ name }}
                  labels {{ nodes {{ name }} }}
                  dueDate createdAt url
                }}
              }}
            }}"""
            data = LinearTool._gql(q, cred_key=cred_key)
            issues = data.get("issues", {}).get("nodes", [])
            return ToolResult(True, f"✓ {len(issues)} issues", issues)
        except Exception as e:
            return ToolResult(False, f"✗ list_issues failed: {e}")

    @staticmethod
    def get_issue(issue_id: str, cred_key: str = "linear") -> ToolResult:
        try:
            q = """
            query($id: String!) {
              issue(id: $id) {
                id title description state { name } priority
                assignee { name email }
                labels { nodes { name } }
                dueDate createdAt updatedAt url
                comments { nodes { id body createdAt user { name } } }
              }
            }"""
            data = LinearTool._gql(q, {"id": issue_id}, cred_key)
            return ToolResult(True, "✓ Issue retrieved", data.get("issue"))
        except Exception as e:
            return ToolResult(False, f"✗ get_issue failed: {e}")

    @staticmethod
    def create_issue(title: str, description: str = "",
                     team_id: str = "", priority: int = 0,
                     assignee_id: str = None, label_ids: list = None,
                     due_date: str = None,
                     cred_key: str = "linear") -> ToolResult:
        try:
            m = """
            mutation($input: IssueCreateInput!) {
              issueCreate(input: $input) {
                success issue { id title url }
              }
            }"""
            inp: dict = {"title": title, "description": description,
                         "teamId": team_id, "priority": priority}
            if assignee_id:
                inp["assigneeId"] = assignee_id
            if label_ids:
                inp["labelIds"] = label_ids
            if due_date:
                inp["dueDate"] = due_date
            data = LinearTool._gql(m, {"input": inp}, cred_key)
            result = data.get("issueCreate", {})
            return ToolResult(result.get("success", False),
                              f"✓ Issue created" if result.get("success")
                              else "✗ Creation failed",
                              result.get("issue"))
        except Exception as e:
            return ToolResult(False, f"✗ create_issue failed: {e}")

    @staticmethod
    def update_issue(id: str, data: dict,
                     cred_key: str = "linear") -> ToolResult:
        try:
            m = """
            mutation($id: String!, $input: IssueUpdateInput!) {
              issueUpdate(id: $id, input: $input) {
                success issue { id title }
              }
            }"""
            resp = LinearTool._gql(m, {"id": id, "input": data}, cred_key)
            result = resp.get("issueUpdate", {})
            return ToolResult(result.get("success", False),
                              "✓ Issue updated" if result.get("success")
                              else "✗ Update failed",
                              result.get("issue"))
        except Exception as e:
            return ToolResult(False, f"✗ update_issue failed: {e}")

    @staticmethod
    def close_issue(id: str, resolution: str = "Done",
                    cred_key: str = "linear") -> ToolResult:
        try:
            # Get the "Done" state id for the issue's team
            q = """
            query($id: String!) {
              issue(id: $id) { team { id } }
            }"""
            d = LinearTool._gql(q, {"id": id}, cred_key)
            team_id = d["issue"]["team"]["id"]
            sq = """
            query($filter: WorkflowStateFilter) {
              workflowStates(filter: $filter) {
                nodes { id name type }
              }
            }"""
            sd = LinearTool._gql(
                sq,
                {"filter": {"team": {"id": {"eq": team_id}},
                            "type": {"eq": "completed"}}},
                cred_key
            )
            states = sd.get("workflowStates", {}).get("nodes", [])
            state_id = states[0]["id"] if states else None
            inp: dict = {}
            if state_id:
                inp["stateId"] = state_id
            return LinearTool.update_issue(id, inp, cred_key)
        except Exception as e:
            return ToolResult(False, f"✗ close_issue failed: {e}")

    @staticmethod
    def delete_issue(id: str, cred_key: str = "linear") -> ToolResult:
        try:
            m = """
            mutation($id: String!) {
              issueDelete(id: $id) { success }
            }"""
            data = LinearTool._gql(m, {"id": id}, cred_key)
            ok = data.get("issueDelete", {}).get("success", False)
            return ToolResult(ok, "✓ Deleted" if ok else "✗ Delete failed")
        except Exception as e:
            return ToolResult(False, f"✗ delete_issue failed: {e}")

    # ── Teams / Projects ──────────────────────────────────────────────────

    @staticmethod
    def list_teams(cred_key: str = "linear") -> ToolResult:
        try:
            q = "query { teams { nodes { id name key description } } }"
            data = LinearTool._gql(q, cred_key=cred_key)
            teams = data.get("teams", {}).get("nodes", [])
            return ToolResult(True, f"✓ {len(teams)} teams", teams)
        except Exception as e:
            return ToolResult(False, f"✗ list_teams failed: {e}")

    @staticmethod
    def get_team(team_id: str, cred_key: str = "linear") -> ToolResult:
        try:
            q = """
            query($id: String!) {
              team(id: $id) { id name key description members { nodes { id name } } }
            }"""
            data = LinearTool._gql(q, {"id": team_id}, cred_key)
            return ToolResult(True, "✓ Team retrieved", data.get("team"))
        except Exception as e:
            return ToolResult(False, f"✗ get_team failed: {e}")

    @staticmethod
    def list_projects(team_id: str = None,
                      cred_key: str = "linear") -> ToolResult:
        try:
            if team_id:
                q = """
                query($id: String!) {
                  team(id: $id) { projects { nodes { id name state description } } }
                }"""
                data = LinearTool._gql(q, {"id": team_id}, cred_key)
                projects = (data.get("team", {})
                            .get("projects", {})
                            .get("nodes", []))
            else:
                q = "query { projects { nodes { id name state } } }"
                data = LinearTool._gql(q, cred_key=cred_key)
                projects = data.get("projects", {}).get("nodes", [])
            return ToolResult(True, f"✓ {len(projects)} projects", projects)
        except Exception as e:
            return ToolResult(False, f"✗ list_projects failed: {e}")

    @staticmethod
    def create_project(name: str, team_id: str, description: str = "",
                       target_date: str = None,
                       cred_key: str = "linear") -> ToolResult:
        try:
            m = """
            mutation($input: ProjectCreateInput!) {
              projectCreate(input: $input) {
                success project { id name url }
              }
            }"""
            inp: dict = {"name": name, "teamIds": [team_id],
                         "description": description}
            if target_date:
                inp["targetDate"] = target_date
            data = LinearTool._gql(m, {"input": inp}, cred_key)
            result = data.get("projectCreate", {})
            return ToolResult(result.get("success", False),
                              "✓ Project created",
                              result.get("project"))
        except Exception as e:
            return ToolResult(False, f"✗ create_project failed: {e}")

    @staticmethod
    def update_project(id: str, data: dict,
                       cred_key: str = "linear") -> ToolResult:
        try:
            m = """
            mutation($id: String!, $input: ProjectUpdateInput!) {
              projectUpdate(id: $id, input: $input) {
                success project { id name }
              }
            }"""
            resp = LinearTool._gql(m, {"id": id, "input": data}, cred_key)
            result = resp.get("projectUpdate", {})
            return ToolResult(result.get("success", False),
                              "✓ Project updated", result.get("project"))
        except Exception as e:
            return ToolResult(False, f"✗ update_project failed: {e}")

    # ── Members / Labels / Cycles ─────────────────────────────────────────

    @staticmethod
    def list_members(team_id: str, cred_key: str = "linear") -> ToolResult:
        try:
            q = """
            query($id: String!) {
              team(id: $id) { members { nodes { id name email } } }
            }"""
            data = LinearTool._gql(q, {"id": team_id}, cred_key)
            members = (data.get("team", {})
                       .get("members", {})
                       .get("nodes", []))
            return ToolResult(True, f"✓ {len(members)} members", members)
        except Exception as e:
            return ToolResult(False, f"✗ list_members failed: {e}")

    @staticmethod
    def list_labels(team_id: str, cred_key: str = "linear") -> ToolResult:
        try:
            q = """
            query($id: String!) {
              team(id: $id) { labels { nodes { id name color } } }
            }"""
            data = LinearTool._gql(q, {"id": team_id}, cred_key)
            labels = (data.get("team", {})
                      .get("labels", {})
                      .get("nodes", []))
            return ToolResult(True, f"✓ {len(labels)} labels", labels)
        except Exception as e:
            return ToolResult(False, f"✗ list_labels failed: {e}")

    @staticmethod
    def create_label(name: str, color: str, team_id: str,
                     cred_key: str = "linear") -> ToolResult:
        try:
            m = """
            mutation($input: IssueLabelCreateInput!) {
              issueLabelCreate(input: $input) {
                success issueLabel { id name color }
              }
            }"""
            data = LinearTool._gql(
                m, {"input": {"name": name, "color": color,
                              "teamId": team_id}}, cred_key)
            result = data.get("issueLabelCreate", {})
            return ToolResult(result.get("success", False),
                              "✓ Label created", result.get("issueLabel"))
        except Exception as e:
            return ToolResult(False, f"✗ create_label failed: {e}")

    @staticmethod
    def list_cycles(team_id: str, cred_key: str = "linear") -> ToolResult:
        try:
            q = """
            query($id: String!) {
              team(id: $id) { cycles { nodes { id name number startsAt endsAt } } }
            }"""
            data = LinearTool._gql(q, {"id": team_id}, cred_key)
            cycles = (data.get("team", {})
                      .get("cycles", {})
                      .get("nodes", []))
            return ToolResult(True, f"✓ {len(cycles)} cycles", cycles)
        except Exception as e:
            return ToolResult(False, f"✗ list_cycles failed: {e}")

    @staticmethod
    def create_cycle(name: str, team_id: str, start_date: str,
                     end_date: str, cred_key: str = "linear") -> ToolResult:
        try:
            m = """
            mutation($input: CycleCreateInput!) {
              cycleCreate(input: $input) {
                success cycle { id name startsAt endsAt }
              }
            }"""
            data = LinearTool._gql(
                m, {"input": {"name": name, "teamId": team_id,
                              "startsAt": start_date,
                              "endsAt": end_date}}, cred_key)
            result = data.get("cycleCreate", {})
            return ToolResult(result.get("success", False),
                              "✓ Cycle created", result.get("cycle"))
        except Exception as e:
            return ToolResult(False, f"✗ create_cycle failed: {e}")

    @staticmethod
    def add_issue_to_cycle(cycle_id: str, issue_id: str,
                           cred_key: str = "linear") -> ToolResult:
        try:
            m = """
            mutation($id: String!, $input: IssueUpdateInput!) {
              issueUpdate(id: $id, input: $input) { success }
            }"""
            data = LinearTool._gql(
                m, {"id": issue_id, "input": {"cycleId": cycle_id}}, cred_key)
            ok = data.get("issueUpdate", {}).get("success", False)
            return ToolResult(ok, "✓ Issue added to cycle" if ok
                              else "✗ Failed")
        except Exception as e:
            return ToolResult(False, f"✗ add_issue_to_cycle failed: {e}")

    # ── Comments ──────────────────────────────────────────────────────────

    @staticmethod
    def get_comments(issue_id: str, cred_key: str = "linear") -> ToolResult:
        try:
            q = """
            query($id: String!) {
              issue(id: $id) {
                comments { nodes { id body createdAt user { name } } }
              }
            }"""
            data = LinearTool._gql(q, {"id": issue_id}, cred_key)
            comments = (data.get("issue", {})
                        .get("comments", {})
                        .get("nodes", []))
            return ToolResult(True, f"✓ {len(comments)} comments", comments)
        except Exception as e:
            return ToolResult(False, f"✗ get_comments failed: {e}")

    @staticmethod
    def add_comment(issue_id: str, body: str,
                    cred_key: str = "linear") -> ToolResult:
        try:
            m = """
            mutation($input: CommentCreateInput!) {
              commentCreate(input: $input) {
                success comment { id body }
              }
            }"""
            data = LinearTool._gql(
                m, {"input": {"issueId": issue_id, "body": body}}, cred_key)
            result = data.get("commentCreate", {})
            return ToolResult(result.get("success", False),
                              "✓ Comment added", result.get("comment"))
        except Exception as e:
            return ToolResult(False, f"✗ add_comment failed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 4. AsanaTool
# ═════════════════════════════════════════════════════════════════════════════

class AsanaTool:
    name = "asana"
    description = (
        "Asana project management — workspaces, projects, tasks, subtasks, "
        "sections, tags, and comments"
    )

    @staticmethod
    def _client(cred_key: str = "asana"):
        import asana
        token = CredStore.load(cred_key).get("access_token", "")
        if not token:
            raise ValueError("No Asana token. Store under 'asana' key.")
        config = asana.Configuration()
        config.access_token = token
        return asana.ApiClient(config)

    @staticmethod
    def list_workspaces(cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.WorkspacesApi(client)
            ws = list(api.get_workspaces({}))
            return ToolResult(True, f"✓ {len(ws)} workspaces", ws)
        except Exception as e:
            return ToolResult(False, f"✗ list_workspaces failed: {e}")

    @staticmethod
    def list_projects(workspace_id: str = None, team_id: str = None,
                      cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.ProjectsApi(client)
            opts: dict = {}
            if workspace_id:
                opts["workspace"] = workspace_id
            if team_id:
                opts["team"] = team_id
            projects = list(api.get_projects(opts))
            return ToolResult(True, f"✓ {len(projects)} projects", projects)
        except Exception as e:
            return ToolResult(False, f"✗ list_projects failed: {e}")

    @staticmethod
    def get_project(project_id: str, cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.ProjectsApi(client)
            proj = api.get_project(project_id, {})
            return ToolResult(True, "✓ Project retrieved", proj)
        except Exception as e:
            return ToolResult(False, f"✗ get_project failed: {e}")

    @staticmethod
    def create_project(name: str, workspace_id: str,
                       team_id: str = None, notes: str = "",
                       color: str = "none", public: bool = True,
                       cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.ProjectsApi(client)
            body: dict = {
                "data": {"name": name, "workspace": workspace_id,
                         "notes": notes, "color": color,
                         "public": public}
            }
            if team_id:
                body["data"]["team"] = team_id
            proj = api.create_project(body, {})
            return ToolResult(True, f"✓ Project created: {proj.get('gid','')}", proj)
        except Exception as e:
            return ToolResult(False, f"✗ create_project failed: {e}")

    @staticmethod
    def list_tasks(project_id: str = None, assignee: str = None,
                   completed: bool = False, due_on: str = None,
                   cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.TasksApi(client)
            opts: dict = {"completed_since": "now" if not completed else ""}
            if project_id:
                opts["project"] = project_id
            if assignee:
                opts["assignee"] = assignee
            if due_on:
                opts["due_on"] = due_on
            tasks = list(api.get_tasks(opts))
            return ToolResult(True, f"✓ {len(tasks)} tasks", tasks)
        except Exception as e:
            return ToolResult(False, f"✗ list_tasks failed: {e}")

    @staticmethod
    def get_task(task_id: str, cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.TasksApi(client)
            task = api.get_task(task_id, {})
            return ToolResult(True, "✓ Task retrieved", task)
        except Exception as e:
            return ToolResult(False, f"✗ get_task failed: {e}")

    @staticmethod
    def create_task(name: str, workspace_id: str,
                    project_id: str = None, assignee: str = None,
                    notes: str = "", due_on: str = None,
                    custom_fields: dict = None,
                    cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.TasksApi(client)
            body: dict = {
                "data": {"name": name, "workspace": workspace_id,
                         "notes": notes}
            }
            if project_id:
                body["data"]["projects"] = [project_id]
            if assignee:
                body["data"]["assignee"] = assignee
            if due_on:
                body["data"]["due_on"] = due_on
            if custom_fields:
                body["data"]["custom_fields"] = custom_fields
            task = api.create_task(body, {})
            return ToolResult(True, f"✓ Task created: {task.get('gid','')}", task)
        except Exception as e:
            return ToolResult(False, f"✗ create_task failed: {e}")

    @staticmethod
    def update_task(id: str, data: dict,
                    cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.TasksApi(client)
            task = api.update_task({"data": data}, id, {})
            return ToolResult(True, "✓ Task updated", task)
        except Exception as e:
            return ToolResult(False, f"✗ update_task failed: {e}")

    @staticmethod
    def complete_task(id: str, cred_key: str = "asana") -> ToolResult:
        return AsanaTool.update_task(id, {"completed": True}, cred_key)

    @staticmethod
    def delete_task(id: str, cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.TasksApi(client)
            api.delete_task(id)
            return ToolResult(True, f"✓ Task deleted: {id}")
        except Exception as e:
            return ToolResult(False, f"✗ delete_task failed: {e}")

    @staticmethod
    def add_subtask(parent_task_id: str, name: str,
                    assignee: str = None, notes: str = "",
                    cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.TasksApi(client)
            body: dict = {"data": {"name": name, "notes": notes}}
            if assignee:
                body["data"]["assignee"] = assignee
            subtask = api.create_subtask_for_task(body, parent_task_id, {})
            return ToolResult(True, f"✓ Subtask created: {subtask.get('gid','')}", subtask)
        except Exception as e:
            return ToolResult(False, f"✗ add_subtask failed: {e}")

    @staticmethod
    def list_subtasks(task_id: str, cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.TasksApi(client)
            subs = list(api.get_subtasks_for_task(task_id, {}))
            return ToolResult(True, f"✓ {len(subs)} subtasks", subs)
        except Exception as e:
            return ToolResult(False, f"✗ list_subtasks failed: {e}")

    @staticmethod
    def add_comment(task_id: str, text: str,
                    cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.StoriesApi(client)
            story = api.create_story_for_task(
                {"data": {"text": text}}, task_id, {})
            return ToolResult(True, "✓ Comment added", story)
        except Exception as e:
            return ToolResult(False, f"✗ add_comment failed: {e}")

    @staticmethod
    def list_comments(task_id: str, cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.StoriesApi(client)
            stories = list(api.get_stories_for_task(task_id, {}))
            comments = [s for s in stories
                        if s.get("type") == "comment"]
            return ToolResult(True, f"✓ {len(comments)} comments", comments)
        except Exception as e:
            return ToolResult(False, f"✗ list_comments failed: {e}")

    @staticmethod
    def list_sections(project_id: str, cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.SectionsApi(client)
            secs = list(api.get_sections_for_project(project_id, {}))
            return ToolResult(True, f"✓ {len(secs)} sections", secs)
        except Exception as e:
            return ToolResult(False, f"✗ list_sections failed: {e}")

    @staticmethod
    def create_section(project_id: str, name: str,
                       cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.SectionsApi(client)
            sec = api.create_section_for_project(
                {"data": {"name": name}}, project_id, {})
            return ToolResult(True, f"✓ Section created: {name}", sec)
        except Exception as e:
            return ToolResult(False, f"✗ create_section failed: {e}")

    @staticmethod
    def move_task_to_section(task_id: str, section_id: str,
                              cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.SectionsApi(client)
            api.add_task_for_section(
                {"data": {"task": task_id}}, section_id, {})
            return ToolResult(True, f"✓ Task moved to section")
        except Exception as e:
            return ToolResult(False, f"✗ move_task_to_section failed: {e}")

    @staticmethod
    def list_tags(workspace_id: str, cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.TagsApi(client)
            tags = list(api.get_tags_for_workspace(workspace_id, {}))
            return ToolResult(True, f"✓ {len(tags)} tags", tags)
        except Exception as e:
            return ToolResult(False, f"✗ list_tags failed: {e}")

    @staticmethod
    def add_tag_to_task(task_id: str, tag_id: str,
                        cred_key: str = "asana") -> ToolResult:
        try:
            import asana
            client = AsanaTool._client(cred_key)
            api = asana.TasksApi(client)
            api.add_tag_for_task({"data": {"tag": tag_id}}, task_id, {})
            return ToolResult(True, f"✓ Tag added to task")
        except Exception as e:
            return ToolResult(False, f"✗ add_tag_to_task failed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 5. TrelloTool
# ═════════════════════════════════════════════════════════════════════════════

class TrelloTool:
    name = "trello"
    description = (
        "Trello board management — boards, lists, cards, checklists, "
        "labels, members, comments, and attachments"
    )

    @staticmethod
    def _api(method: str, path: str, cred_key: str = "trello",
             **kwargs) -> Any:
        import requests
        creds = CredStore.load(cred_key)
        key = creds.get("api_key", "")
        token = creds.get("token", "")
        if not key or not token:
            raise ValueError("No Trello credentials. Store 'api_key' and 'token' under 'trello'.")
        url = f"https://api.trello.com/1/{path.lstrip('/')}"
        params = kwargs.pop("params", {})
        params.update({"key": key, "token": token})
        fn = getattr(requests, method.lower())
        resp = fn(url, params=params, timeout=20, **kwargs)
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    @staticmethod
    def list_boards(member_id: str = "me",
                    cred_key: str = "trello") -> ToolResult:
        try:
            boards = TrelloTool._api(
                "get", f"members/{member_id}/boards",
                cred_key,
                params={"fields": "id,name,desc,url,closed"})
            return ToolResult(True, f"✓ {len(boards)} boards", boards)
        except Exception as e:
            return ToolResult(False, f"✗ list_boards failed: {e}")

    @staticmethod
    def get_board(board_id: str, cred_key: str = "trello") -> ToolResult:
        try:
            board = TrelloTool._api("get", f"boards/{board_id}", cred_key)
            return ToolResult(True, "✓ Board retrieved", board)
        except Exception as e:
            return ToolResult(False, f"✗ get_board failed: {e}")

    @staticmethod
    def create_board(name: str, desc: str = "",
                     default_lists: bool = True,
                     cred_key: str = "trello") -> ToolResult:
        try:
            board = TrelloTool._api(
                "post", "boards", cred_key,
                json={"name": name, "desc": desc,
                      "defaultLists": default_lists})
            return ToolResult(True, f"✓ Board created: {board.get('id')}", board)
        except Exception as e:
            return ToolResult(False, f"✗ create_board failed: {e}")

    @staticmethod
    def list_lists(board_id: str, cred_key: str = "trello") -> ToolResult:
        try:
            lists = TrelloTool._api("get", f"boards/{board_id}/lists",
                                    cred_key)
            return ToolResult(True, f"✓ {len(lists)} lists", lists)
        except Exception as e:
            return ToolResult(False, f"✗ list_lists failed: {e}")

    @staticmethod
    def create_list(board_id: str, name: str, pos: str = "bottom",
                    cred_key: str = "trello") -> ToolResult:
        try:
            lst = TrelloTool._api(
                "post", "lists", cred_key,
                json={"name": name, "idBoard": board_id, "pos": pos})
            return ToolResult(True, f"✓ List created: {lst.get('id')}", lst)
        except Exception as e:
            return ToolResult(False, f"✗ create_list failed: {e}")

    @staticmethod
    def archive_list(list_id: str, cred_key: str = "trello") -> ToolResult:
        try:
            TrelloTool._api("put", f"lists/{list_id}/closed", cred_key,
                            json={"value": True})
            return ToolResult(True, f"✓ List archived: {list_id}")
        except Exception as e:
            return ToolResult(False, f"✗ archive_list failed: {e}")

    @staticmethod
    def list_cards(list_or_board_id: str, filter: str = "open",
                   cred_key: str = "trello") -> ToolResult:
        try:
            # Try list first, fall back to board
            try:
                cards = TrelloTool._api(
                    "get", f"lists/{list_or_board_id}/cards",
                    cred_key, params={"filter": filter})
            except Exception:
                cards = TrelloTool._api(
                    "get", f"boards/{list_or_board_id}/cards",
                    cred_key, params={"filter": filter})
            return ToolResult(True, f"✓ {len(cards)} cards", cards)
        except Exception as e:
            return ToolResult(False, f"✗ list_cards failed: {e}")

    @staticmethod
    def get_card(card_id: str, cred_key: str = "trello") -> ToolResult:
        try:
            card = TrelloTool._api("get", f"cards/{card_id}", cred_key)
            return ToolResult(True, "✓ Card retrieved", card)
        except Exception as e:
            return ToolResult(False, f"✗ get_card failed: {e}")

    @staticmethod
    def create_card(list_id: str, name: str, desc: str = "",
                    due: str = None, labels: list = None,
                    members: list = None, attachments: list = None,
                    cred_key: str = "trello") -> ToolResult:
        try:
            body: dict = {"idList": list_id, "name": name, "desc": desc}
            if due:
                body["due"] = due
            if labels:
                body["idLabels"] = labels
            if members:
                body["idMembers"] = members
            card = TrelloTool._api("post", "cards", cred_key, json=body)
            if attachments:
                for att in attachments:
                    TrelloTool._api(
                        "post", f"cards/{card['id']}/attachments",
                        cred_key, json={"url": att, "name": att})
            return ToolResult(True, f"✓ Card created: {card.get('id')}", card)
        except Exception as e:
            return ToolResult(False, f"✗ create_card failed: {e}")

    @staticmethod
    def update_card(id: str, data: dict,
                    cred_key: str = "trello") -> ToolResult:
        try:
            card = TrelloTool._api("put", f"cards/{id}", cred_key, json=data)
            return ToolResult(True, "✓ Card updated", card)
        except Exception as e:
            return ToolResult(False, f"✗ update_card failed: {e}")

    @staticmethod
    def move_card(card_id: str, list_id: str,
                  cred_key: str = "trello") -> ToolResult:
        return TrelloTool.update_card(card_id, {"idList": list_id}, cred_key)

    @staticmethod
    def archive_card(card_id: str, cred_key: str = "trello") -> ToolResult:
        return TrelloTool.update_card(card_id, {"closed": True}, cred_key)

    @staticmethod
    def add_checklist(card_id: str, name: str, items: list = None,
                      cred_key: str = "trello") -> ToolResult:
        try:
            cl = TrelloTool._api(
                "post", "checklists", cred_key,
                json={"idCard": card_id, "name": name})
            cl_id = cl["id"]
            for item in (items or []):
                TrelloTool._api(
                    "post", f"checklists/{cl_id}/checkItems",
                    cred_key, json={"name": item})
            return ToolResult(True, f"✓ Checklist '{name}' added", cl)
        except Exception as e:
            return ToolResult(False, f"✗ add_checklist failed: {e}")

    @staticmethod
    def check_checklist_item(card_id: str, checklist_id: str,
                              item_id: str, checked: bool = True,
                              cred_key: str = "trello") -> ToolResult:
        try:
            state = "complete" if checked else "incomplete"
            TrelloTool._api(
                "put",
                f"cards/{card_id}/checkItem/{item_id}",
                cred_key, json={"state": state})
            return ToolResult(True, f"✓ Item marked {state}")
        except Exception as e:
            return ToolResult(False, f"✗ check_checklist_item failed: {e}")

    @staticmethod
    def add_comment(card_id: str, text: str,
                    cred_key: str = "trello") -> ToolResult:
        try:
            resp = TrelloTool._api(
                "post", f"cards/{card_id}/actions/comments",
                cred_key, json={"text": text})
            return ToolResult(True, "✓ Comment added", resp)
        except Exception as e:
            return ToolResult(False, f"✗ add_comment failed: {e}")

    @staticmethod
    def add_attachment(card_id: str, url_or_path: str,
                       name: str = "", cred_key: str = "trello") -> ToolResult:
        try:
            import requests as req
            p = Path(url_or_path)
            creds = CredStore.load(cred_key)
            key = creds.get("api_key", "")
            token_val = creds.get("token", "")
            url = f"https://api.trello.com/1/cards/{card_id}/attachments"
            if p.exists():
                with open(url_or_path, "rb") as f:
                    resp = req.post(url,
                                    params={"key": key, "token": token_val},
                                    files={"file": (name or p.name, f)},
                                    timeout=30)
            else:
                resp = req.post(url,
                                params={"key": key, "token": token_val},
                                json={"url": url_or_path, "name": name},
                                timeout=20)
            resp.raise_for_status()
            return ToolResult(True, "✓ Attachment added", resp.json())
        except Exception as e:
            return ToolResult(False, f"✗ add_attachment failed: {e}")

    @staticmethod
    def list_members(board_id: str, cred_key: str = "trello") -> ToolResult:
        try:
            members = TrelloTool._api(
                "get", f"boards/{board_id}/members", cred_key)
            return ToolResult(True, f"✓ {len(members)} members", members)
        except Exception as e:
            return ToolResult(False, f"✗ list_members failed: {e}")

    @staticmethod
    def add_member(board_id: str, email: str, type: str = "normal",
                   cred_key: str = "trello") -> ToolResult:
        try:
            resp = TrelloTool._api(
                "put", f"boards/{board_id}/members", cred_key,
                json={"email": email, "type": type})
            return ToolResult(True, f"✓ Member {email} added", resp)
        except Exception as e:
            return ToolResult(False, f"✗ add_member failed: {e}")

    @staticmethod
    def create_label(board_id: str, name: str, color: str,
                     cred_key: str = "trello") -> ToolResult:
        try:
            label = TrelloTool._api(
                "post", "labels", cred_key,
                json={"name": name, "color": color,
                      "idBoard": board_id})
            return ToolResult(True, f"✓ Label created: {label.get('id')}", label)
        except Exception as e:
            return ToolResult(False, f"✗ create_label failed: {e}")

    @staticmethod
    def add_label_to_card(card_id: str, label_id: str,
                           cred_key: str = "trello") -> ToolResult:
        try:
            TrelloTool._api(
                "post", f"cards/{card_id}/idLabels",
                cred_key, json={"value": label_id})
            return ToolResult(True, "✓ Label added to card")
        except Exception as e:
            return ToolResult(False, f"✗ add_label_to_card failed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 6. ClickUpTool
# ═════════════════════════════════════════════════════════════════════════════

class ClickUpTool:
    name = "clickup"
    description = (
        "ClickUp workspace management — spaces, folders, lists, tasks, "
        "comments, checklists, time tracking, and views"
    )

    @staticmethod
    def _api(method: str, path: str, cred_key: str = "clickup",
             **kwargs) -> Any:
        import requests
        token = CredStore.load(cred_key).get("api_token", "")
        if not token:
            raise ValueError("No ClickUp token. Store under 'clickup' key.")
        url = f"https://api.clickup.com/api/v2/{path.lstrip('/')}"
        headers = {"Authorization": token, "Content-Type": "application/json"}
        fn = getattr(requests, method.lower())
        resp = fn(url, headers=headers, timeout=20, **kwargs)
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    @staticmethod
    def list_spaces(team_id: str, cred_key: str = "clickup") -> ToolResult:
        try:
            data = ClickUpTool._api("get", f"team/{team_id}/space", cred_key,
                                    params={"archived": "false"})
            spaces = data.get("spaces", [])
            return ToolResult(True, f"✓ {len(spaces)} spaces", spaces)
        except Exception as e:
            return ToolResult(False, f"✗ list_spaces failed: {e}")

    @staticmethod
    def list_folders(space_id: str, cred_key: str = "clickup") -> ToolResult:
        try:
            data = ClickUpTool._api("get", f"space/{space_id}/folder",
                                    cred_key, params={"archived": "false"})
            folders = data.get("folders", [])
            return ToolResult(True, f"✓ {len(folders)} folders", folders)
        except Exception as e:
            return ToolResult(False, f"✗ list_folders failed: {e}")

    @staticmethod
    def list_lists(folder_id: str, cred_key: str = "clickup") -> ToolResult:
        try:
            data = ClickUpTool._api("get", f"folder/{folder_id}/list",
                                    cred_key, params={"archived": "false"})
            lists = data.get("lists", [])
            return ToolResult(True, f"✓ {len(lists)} lists", lists)
        except Exception as e:
            return ToolResult(False, f"✗ list_lists failed: {e}")

    @staticmethod
    def get_tasks(list_id: str, assignees: list = None,
                  statuses: list = None, due_date: str = None,
                  page: int = 0, cred_key: str = "clickup") -> ToolResult:
        try:
            params: dict = {"page": page}
            if assignees:
                params["assignees[]"] = assignees
            if statuses:
                params["statuses[]"] = statuses
            if due_date:
                params["due_date_gt"] = 0
            data = ClickUpTool._api("get", f"list/{list_id}/task",
                                    cred_key, params=params)
            tasks = data.get("tasks", [])
            return ToolResult(True, f"✓ {len(tasks)} tasks", tasks)
        except Exception as e:
            return ToolResult(False, f"✗ get_tasks failed: {e}")

    @staticmethod
    def get_task(task_id: str, cred_key: str = "clickup") -> ToolResult:
        try:
            task = ClickUpTool._api("get", f"task/{task_id}", cred_key)
            return ToolResult(True, "✓ Task retrieved", task)
        except Exception as e:
            return ToolResult(False, f"✗ get_task failed: {e}")

    @staticmethod
    def create_task(list_id: str, name: str, description: str = "",
                    assignees: list = None, status: str = None,
                    priority: int = None, due_date: str = None,
                    tags: list = None, cred_key: str = "clickup") -> ToolResult:
        try:
            body: dict = {"name": name, "description": description}
            if assignees:
                body["assignees"] = assignees
            if status:
                body["status"] = status
            if priority is not None:
                body["priority"] = priority
            if due_date:
                # convert ISO date to ms timestamp
                dt = datetime.fromisoformat(due_date)
                body["due_date"] = int(dt.timestamp() * 1000)
            if tags:
                body["tags"] = tags
            task = ClickUpTool._api("post", f"list/{list_id}/task",
                                    cred_key, json=body)
            return ToolResult(True, f"✓ Task created: {task.get('id')}", task)
        except Exception as e:
            return ToolResult(False, f"✗ create_task failed: {e}")

    @staticmethod
    def update_task(id: str, data: dict,
                    cred_key: str = "clickup") -> ToolResult:
        try:
            task = ClickUpTool._api("put", f"task/{id}", cred_key, json=data)
            return ToolResult(True, "✓ Task updated", task)
        except Exception as e:
            return ToolResult(False, f"✗ update_task failed: {e}")

    @staticmethod
    def delete_task(id: str, cred_key: str = "clickup") -> ToolResult:
        try:
            ClickUpTool._api("delete", f"task/{id}", cred_key)
            return ToolResult(True, f"✓ Task deleted: {id}")
        except Exception as e:
            return ToolResult(False, f"✗ delete_task failed: {e}")

    @staticmethod
    def set_task_status(id: str, status: str,
                        cred_key: str = "clickup") -> ToolResult:
        return ClickUpTool.update_task(id, {"status": status}, cred_key)

    @staticmethod
    def add_comment(task_id: str, comment_text: str,
                    notify_all: bool = False,
                    cred_key: str = "clickup") -> ToolResult:
        try:
            resp = ClickUpTool._api(
                "post", f"task/{task_id}/comment", cred_key,
                json={"comment_text": comment_text,
                      "notify_all": notify_all})
            return ToolResult(True, "✓ Comment added", resp)
        except Exception as e:
            return ToolResult(False, f"✗ add_comment failed: {e}")

    @staticmethod
    def list_comments(task_id: str, cred_key: str = "clickup") -> ToolResult:
        try:
            data = ClickUpTool._api("get", f"task/{task_id}/comment", cred_key)
            comments = data.get("comments", [])
            return ToolResult(True, f"✓ {len(comments)} comments", comments)
        except Exception as e:
            return ToolResult(False, f"✗ list_comments failed: {e}")

    @staticmethod
    def create_checklist(task_id: str, name: str,
                         cred_key: str = "clickup") -> ToolResult:
        try:
            resp = ClickUpTool._api(
                "post", f"task/{task_id}/checklist",
                cred_key, json={"name": name})
            return ToolResult(True, f"✓ Checklist created",
                              resp.get("checklist"))
        except Exception as e:
            return ToolResult(False, f"✗ create_checklist failed: {e}")

    @staticmethod
    def add_checklist_item(checklist_id: str, name: str,
                           assignee: str = None,
                           cred_key: str = "clickup") -> ToolResult:
        try:
            body: dict = {"name": name}
            if assignee:
                body["assignee"] = assignee
            resp = ClickUpTool._api(
                "post", f"checklist/{checklist_id}/checklist_item",
                cred_key, json=body)
            return ToolResult(True, "✓ Checklist item added", resp)
        except Exception as e:
            return ToolResult(False, f"✗ add_checklist_item failed: {e}")

    @staticmethod
    def track_time(task_id: str, duration: int,
                   start: str = None, end: str = None,
                   description: str = "",
                   cred_key: str = "clickup") -> ToolResult:
        try:
            body: dict = {"duration": duration, "description": description}
            if start:
                dt = datetime.fromisoformat(start)
                body["start"] = int(dt.timestamp() * 1000)
            if end:
                dt = datetime.fromisoformat(end)
                body["end"] = int(dt.timestamp() * 1000)
            resp = ClickUpTool._api(
                "post", f"task/{task_id}/time", cred_key, json=body)
            return ToolResult(True, "✓ Time tracked", resp)
        except Exception as e:
            return ToolResult(False, f"✗ track_time failed: {e}")

    @staticmethod
    def get_time_entries(task_id: str, cred_key: str = "clickup") -> ToolResult:
        try:
            data = ClickUpTool._api("get", f"task/{task_id}/time", cred_key)
            entries = data.get("data", [])
            return ToolResult(True, f"✓ {len(entries)} time entries", entries)
        except Exception as e:
            return ToolResult(False, f"✗ get_time_entries failed: {e}")

    @staticmethod
    def list_views(list_id: str, cred_key: str = "clickup") -> ToolResult:
        try:
            data = ClickUpTool._api("get", f"list/{list_id}/view", cred_key)
            views = data.get("views", [])
            return ToolResult(True, f"✓ {len(views)} views", views)
        except Exception as e:
            return ToolResult(False, f"✗ list_views failed: {e}")

    @staticmethod
    def get_view_tasks(view_id: str, cred_key: str = "clickup") -> ToolResult:
        try:
            data = ClickUpTool._api("get", f"view/{view_id}/task", cred_key)
            tasks = data.get("tasks", [])
            return ToolResult(True, f"✓ {len(tasks)} tasks in view", tasks)
        except Exception as e:
            return ToolResult(False, f"✗ get_view_tasks failed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 7. TodoistTool
# ═════════════════════════════════════════════════════════════════════════════

class TodoistTool:
    name = "todoist"
    description = (
        "Todoist task and project management — projects, tasks, labels, "
        "comments, quick-add, activity log, and productivity stats"
    )

    @staticmethod
    def _api(cred_key: str = "todoist"):
        from todoist_api_python.api import TodoistAPI
        token = CredStore.load(cred_key).get("api_token", "")
        if not token:
            raise ValueError("No Todoist token. Store under 'todoist' key.")
        return TodoistAPI(token)

    @staticmethod
    def get_projects(cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            projects = api.get_projects()
            data = [{"id": p.id, "name": p.name,
                     "color": p.color} for p in projects]
            return ToolResult(True, f"✓ {len(data)} projects", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_projects failed: {e}")

    @staticmethod
    def add_project(name: str, color: str = "charcoal",
                    parent_id: str = None,
                    cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            kwargs: dict = {"name": name, "color": color}
            if parent_id:
                kwargs["parent_id"] = parent_id
            proj = api.add_project(**kwargs)
            return ToolResult(True, f"✓ Project created: {proj.id}",
                              {"id": proj.id, "name": proj.name})
        except Exception as e:
            return ToolResult(False, f"✗ add_project failed: {e}")

    @staticmethod
    def update_project(id: str, data: dict,
                       cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            ok = api.update_project(id, **data)
            return ToolResult(ok, "✓ Project updated" if ok else "✗ Update failed")
        except Exception as e:
            return ToolResult(False, f"✗ update_project failed: {e}")

    @staticmethod
    def delete_project(id: str, cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            ok = api.delete_project(id)
            return ToolResult(ok, "✓ Project deleted" if ok else "✗ Delete failed")
        except Exception as e:
            return ToolResult(False, f"✗ delete_project failed: {e}")

    @staticmethod
    def get_tasks(project_id: str = None, filter: str = None,
                  label: str = None, priority: int = None,
                  cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            kwargs: dict = {}
            if project_id:
                kwargs["project_id"] = project_id
            if filter:
                kwargs["filter"] = filter
            if label:
                kwargs["label"] = label
            if priority is not None:
                kwargs["priority"] = priority
            tasks = api.get_tasks(**kwargs)
            data = [{"id": t.id, "content": t.content,
                     "due": t.due, "priority": t.priority,
                     "project_id": t.project_id} for t in tasks]
            return ToolResult(True, f"✓ {len(data)} tasks", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_tasks failed: {e}")

    @staticmethod
    def add_task(content: str, description: str = "",
                 project_id: str = None, due_string: str = None,
                 priority: int = 1, labels: list = None,
                 cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            kwargs: dict = {"content": content, "description": description,
                            "priority": priority}
            if project_id:
                kwargs["project_id"] = project_id
            if due_string:
                kwargs["due_string"] = due_string
            if labels:
                kwargs["labels"] = labels
            task = api.add_task(**kwargs)
            return ToolResult(True, f"✓ Task added: {task.id}",
                              {"id": task.id, "content": task.content})
        except Exception as e:
            return ToolResult(False, f"✗ add_task failed: {e}")

    @staticmethod
    def update_task(id: str, data: dict,
                    cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            ok = api.update_task(id, **data)
            return ToolResult(ok, "✓ Task updated" if ok else "✗ Update failed")
        except Exception as e:
            return ToolResult(False, f"✗ update_task failed: {e}")

    @staticmethod
    def complete_task(id: str, cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            ok = api.close_task(id)
            return ToolResult(ok, "✓ Task completed" if ok else "✗ Failed")
        except Exception as e:
            return ToolResult(False, f"✗ complete_task failed: {e}")

    @staticmethod
    def delete_task(id: str, cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            ok = api.delete_task(id)
            return ToolResult(ok, "✓ Task deleted" if ok else "✗ Failed")
        except Exception as e:
            return ToolResult(False, f"✗ delete_task failed: {e}")

    @staticmethod
    def reopen_task(id: str, cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            ok = api.reopen_task(id)
            return ToolResult(ok, "✓ Task reopened" if ok else "✗ Failed")
        except Exception as e:
            return ToolResult(False, f"✗ reopen_task failed: {e}")

    @staticmethod
    def get_comments(task_id: str, cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            comments = api.get_comments(task_id=task_id)
            data = [{"id": c.id, "content": c.content,
                     "posted_at": c.posted_at} for c in comments]
            return ToolResult(True, f"✓ {len(data)} comments", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_comments failed: {e}")

    @staticmethod
    def add_comment(task_id: str, content: str,
                    attachment: dict = None,
                    cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            kwargs: dict = {"task_id": task_id, "content": content}
            if attachment:
                kwargs["attachment"] = attachment
            comment = api.add_comment(**kwargs)
            return ToolResult(True, f"✓ Comment added: {comment.id}",
                              {"id": comment.id})
        except Exception as e:
            return ToolResult(False, f"✗ add_comment failed: {e}")

    @staticmethod
    def get_labels(cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            labels = api.get_labels()
            data = [{"id": l.id, "name": l.name,
                     "color": l.color} for l in labels]
            return ToolResult(True, f"✓ {len(data)} labels", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_labels failed: {e}")

    @staticmethod
    def add_label(name: str, color: str = "charcoal",
                  cred_key: str = "todoist") -> ToolResult:
        try:
            api = TodoistTool._api(cred_key)
            label = api.add_label(name=name, color=color)
            return ToolResult(True, f"✓ Label added: {label.id}",
                              {"id": label.id, "name": label.name})
        except Exception as e:
            return ToolResult(False, f"✗ add_label failed: {e}")

    @staticmethod
    def quick_add(text: str, cred_key: str = "todoist") -> ToolResult:
        """Natural language quick add, e.g. 'Buy milk tomorrow p1 #shopping'"""
        try:
            import requests
            token = CredStore.load(cred_key).get("api_token", "")
            resp = requests.post(
                "https://api.todoist.com/sync/v9/quick/add",
                headers={"Authorization": f"Bearer {token}"},
                json={"text": text}, timeout=10)
            resp.raise_for_status()
            item = resp.json()
            return ToolResult(True, f"✓ Quick-added: {item.get('content','')}", item)
        except Exception as e:
            return ToolResult(False, f"✗ quick_add failed: {e}")

    @staticmethod
    def get_activity_log(event_type: str = None, object_type: str = None,
                         since: str = None,
                         cred_key: str = "todoist") -> ToolResult:
        try:
            import requests
            token = CredStore.load(cred_key).get("api_token", "")
            params: dict = {"limit": 50}
            if event_type:
                params["event_type"] = event_type
            if object_type:
                params["object_type"] = object_type
            if since:
                params["since"] = since
            resp = requests.get(
                "https://api.todoist.com/sync/v9/activity/get",
                headers={"Authorization": f"Bearer {token}"},
                params=params, timeout=15)
            resp.raise_for_status()
            events = resp.json().get("events", [])
            return ToolResult(True, f"✓ {len(events)} events", events)
        except Exception as e:
            return ToolResult(False, f"✗ get_activity_log failed: {e}")

    @staticmethod
    def get_productivity_stats(cred_key: str = "todoist") -> ToolResult:
        try:
            import requests
            token = CredStore.load(cred_key).get("api_token", "")
            resp = requests.get(
                "https://api.todoist.com/sync/v9/user/get_productivity_stats",
                headers={"Authorization": f"Bearer {token}"},
                timeout=15)
            resp.raise_for_status()
            return ToolResult(True, "✓ Stats retrieved", resp.json())
        except Exception as e:
            return ToolResult(False, f"✗ get_productivity_stats failed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 8. ObsidianTool
# ═════════════════════════════════════════════════════════════════════════════

class ObsidianTool:
    name = "obsidian"
    description = (
        "Obsidian vault operations — read/write/search notes, manage tags, "
        "backlinks, daily notes, canvases, and sync folders to vault"
    )

    @staticmethod
    def _note_path(vault_path: str, note_path: str) -> Path:
        p = Path(vault_path) / note_path
        if not str(p).endswith(".md"):
            p = Path(str(p) + ".md")
        return p

    @staticmethod
    def read_note(vault_path: str, note_path: str) -> ToolResult:
        try:
            import frontmatter
            p = ObsidianTool._note_path(vault_path, note_path)
            if not p.exists():
                return ToolResult(False, f"✗ Note not found: {p}")
            post = frontmatter.load(str(p))
            return ToolResult(True, f"✓ Read {p.name}",
                              {"frontmatter": dict(post.metadata),
                               "content": post.content,
                               "raw": p.read_text(encoding="utf-8")})
        except Exception as e:
            return ToolResult(False, f"✗ read_note failed: {e}")

    @staticmethod
    def create_note(vault_path: str, note_path: str, content: str,
                    frontmatter_data: dict = None) -> ToolResult:
        try:
            import frontmatter
            p = ObsidianTool._note_path(vault_path, note_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if p.exists():
                return ToolResult(False, f"✗ Note already exists: {p}")
            post = frontmatter.Post(content,
                                    **(frontmatter_data or {}))
            p.write_text(frontmatter.dumps(post), encoding="utf-8")
            return ToolResult(True, f"✓ Note created: {p}")
        except Exception as e:
            return ToolResult(False, f"✗ create_note failed: {e}")

    @staticmethod
    def update_note(vault_path: str, note_path: str, content: str,
                    merge_mode: str = "replace") -> ToolResult:
        """merge_mode: replace | append | prepend"""
        try:
            import frontmatter
            p = ObsidianTool._note_path(vault_path, note_path)
            if not p.exists():
                return ObsidianTool.create_note(vault_path, note_path, content)
            post = frontmatter.load(str(p))
            if merge_mode == "append":
                post.content = post.content + "\n" + content
            elif merge_mode == "prepend":
                post.content = content + "\n" + post.content
            else:
                post.content = content
            p.write_text(frontmatter.dumps(post), encoding="utf-8")
            return ToolResult(True, f"✓ Note updated ({merge_mode}): {p}")
        except Exception as e:
            return ToolResult(False, f"✗ update_note failed: {e}")

    @staticmethod
    def delete_note(vault_path: str, note_path: str) -> ToolResult:
        try:
            p = ObsidianTool._note_path(vault_path, note_path)
            if p.exists():
                p.unlink()
                return ToolResult(True, f"✓ Deleted: {p}")
            return ToolResult(False, f"✗ Not found: {p}")
        except Exception as e:
            return ToolResult(False, f"✗ delete_note failed: {e}")

    @staticmethod
    def search_notes(vault_path: str, query: str = "",
                     tags: list = None,
                     frontmatter_filter: dict = None) -> ToolResult:
        try:
            import frontmatter as fm
            vault = Path(vault_path)
            results = []
            for md in vault.rglob("*.md"):
                try:
                    post = fm.load(str(md))
                    text = post.content.lower()
                    meta = {k.lower(): v
                            for k, v in post.metadata.items()}

                    # text query
                    if query and query.lower() not in text:
                        if query.lower() not in md.name.lower():
                            continue

                    # tag filter
                    if tags:
                        note_tags = meta.get("tags", [])
                        if isinstance(note_tags, str):
                            note_tags = [note_tags]
                        if not any(t in note_tags for t in tags):
                            continue

                    # frontmatter filter
                    if frontmatter_filter:
                        match = all(
                            str(meta.get(k, "")).lower() == str(v).lower()
                            for k, v in frontmatter_filter.items()
                        )
                        if not match:
                            continue

                    results.append({
                        "path": str(md.relative_to(vault)),
                        "title": md.stem,
                        "tags": meta.get("tags", []),
                    })
                except Exception:
                    continue
            return ToolResult(True, f"✓ {len(results)} notes found", results)
        except Exception as e:
            return ToolResult(False, f"✗ search_notes failed: {e}")

    @staticmethod
    def list_notes(vault_path: str, folder: str = "",
                   recursive: bool = True) -> ToolResult:
        try:
            base = Path(vault_path) / folder
            if not base.exists():
                return ToolResult(False, f"✗ Folder not found: {base}")
            fn = base.rglob if recursive else base.glob
            notes = [str(p.relative_to(vault_path))
                     for p in fn("*.md")]
            return ToolResult(True, f"✓ {len(notes)} notes", notes)
        except Exception as e:
            return ToolResult(False, f"✗ list_notes failed: {e}")

    @staticmethod
    def get_backlinks(vault_path: str, note_path: str) -> ToolResult:
        try:
            target = ObsidianTool._note_path(vault_path, note_path)
            note_name = target.stem
            vault = Path(vault_path)
            backlinks = []
            patterns = [f"[[{note_name}]]",
                        f"[[{note_name}|",
                        f"[{note_name}]"]
            for md in vault.rglob("*.md"):
                if md == target:
                    continue
                try:
                    text = md.read_text(encoding="utf-8", errors="replace")
                    if any(p in text for p in patterns):
                        backlinks.append(str(md.relative_to(vault)))
                except Exception:
                    continue
            return ToolResult(True, f"✓ {len(backlinks)} backlinks", backlinks)
        except Exception as e:
            return ToolResult(False, f"✗ get_backlinks failed: {e}")

    @staticmethod
    def get_outlinks(vault_path: str, note_path: str) -> ToolResult:
        try:
            p = ObsidianTool._note_path(vault_path, note_path)
            text = p.read_text(encoding="utf-8", errors="replace")
            links = re.findall(r'\[\[([^\]|#]+)', text)
            unique = list(dict.fromkeys(links))
            return ToolResult(True, f"✓ {len(unique)} outlinks", unique)
        except Exception as e:
            return ToolResult(False, f"✗ get_outlinks failed: {e}")

    @staticmethod
    def add_tag(vault_path: str, note_path: str,
                tags: list) -> ToolResult:
        try:
            import frontmatter
            p = ObsidianTool._note_path(vault_path, note_path)
            post = frontmatter.load(str(p))
            existing = post.metadata.get("tags", [])
            if isinstance(existing, str):
                existing = [existing]
            merged = list(dict.fromkeys(existing + tags))
            post.metadata["tags"] = merged
            p.write_text(frontmatter.dumps(post), encoding="utf-8")
            return ToolResult(True, f"✓ Tags added: {tags}")
        except Exception as e:
            return ToolResult(False, f"✗ add_tag failed: {e}")

    @staticmethod
    def remove_tag(vault_path: str, note_path: str,
                   tags: list) -> ToolResult:
        try:
            import frontmatter
            p = ObsidianTool._note_path(vault_path, note_path)
            post = frontmatter.load(str(p))
            existing = post.metadata.get("tags", [])
            if isinstance(existing, str):
                existing = [existing]
            post.metadata["tags"] = [t for t in existing
                                     if t not in tags]
            p.write_text(frontmatter.dumps(post), encoding="utf-8")
            return ToolResult(True, f"✓ Tags removed: {tags}")
        except Exception as e:
            return ToolResult(False, f"✗ remove_tag failed: {e}")

    @staticmethod
    def create_daily_note(vault_path: str, date: str = None,
                          template: str = "") -> ToolResult:
        try:
            day = date or datetime.now().strftime("%Y-%m-%d")
            note_path = f"Daily/{day}"
            content = template or f"# {day}\n\n## Tasks\n\n## Notes\n"
            return ObsidianTool.create_note(
                vault_path, note_path, content,
                {"date": day, "tags": ["daily"]})
        except Exception as e:
            return ToolResult(False, f"✗ create_daily_note failed: {e}")

    @staticmethod
    def append_to_daily_note(vault_path: str, content: str,
                              date: str = None) -> ToolResult:
        try:
            day = date or datetime.now().strftime("%Y-%m-%d")
            note_path = f"Daily/{day}"
            p = ObsidianTool._note_path(vault_path, note_path)
            if not p.exists():
                ObsidianTool.create_daily_note(vault_path, day)
            return ObsidianTool.update_note(
                vault_path, note_path, content, merge_mode="append")
        except Exception as e:
            return ToolResult(False, f"✗ append_to_daily_note failed: {e}")

    @staticmethod
    def create_canvas(vault_path: str, canvas_path: str,
                      nodes: list, edges: list = None) -> ToolResult:
        """
        nodes: [{"id":"1","type":"text","text":"Hello","x":0,"y":0,"width":200,"height":60}]
        edges: [{"id":"e1","fromNode":"1","toNode":"2","fromSide":"right","toSide":"left"}]
        """
        try:
            p = Path(vault_path) / canvas_path
            if not str(p).endswith(".canvas"):
                p = Path(str(p) + ".canvas")
            p.parent.mkdir(parents=True, exist_ok=True)
            canvas_data = {"nodes": nodes, "edges": edges or []}
            p.write_text(json.dumps(canvas_data, indent=2), encoding="utf-8")
            return ToolResult(True, f"✓ Canvas created: {p}")
        except Exception as e:
            return ToolResult(False, f"✗ create_canvas failed: {e}")

    @staticmethod
    def get_graph_data(vault_path: str) -> ToolResult:
        """Returns nodes and edges for the full vault graph."""
        try:
            vault = Path(vault_path)
            nodes = []
            edges = []
            all_notes = {p.stem: str(p.relative_to(vault))
                         for p in vault.rglob("*.md")}
            for md in vault.rglob("*.md"):
                try:
                    stem = md.stem
                    rel = str(md.relative_to(vault))
                    nodes.append({"id": stem, "path": rel})
                    text = md.read_text(encoding="utf-8", errors="replace")
                    links = re.findall(r'\[\[([^\]|#]+)', text)
                    for lk in links:
                        lk = lk.strip()
                        if lk in all_notes:
                            edges.append({"from": stem, "to": lk})
                except Exception:
                    continue
            return ToolResult(True, f"✓ Graph: {len(nodes)} nodes, {len(edges)} edges",
                              {"nodes": nodes, "edges": edges})
        except Exception as e:
            return ToolResult(False, f"✗ get_graph_data failed: {e}")

    @staticmethod
    def sync_folder_to_vault(local_folder: str, vault_path: str,
                              subfolder: str = "",
                              file_types: list = None) -> ToolResult:
        try:
            exts = file_types or [".md", ".txt", ".png", ".jpg", ".pdf"]
            src = Path(local_folder)
            dest_base = Path(vault_path) / subfolder
            dest_base.mkdir(parents=True, exist_ok=True)
            copied = 0
            for ext in exts:
                for f in src.rglob(f"*{ext}"):
                    rel = f.relative_to(src)
                    dest = dest_base / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.copy2(str(f), str(dest))
                    copied += 1
            return ToolResult(True, f"✓ Synced {copied} files to vault")
        except Exception as e:
            return ToolResult(False, f"✗ sync_folder_to_vault failed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 9. BookmarkManagerTool
# ═════════════════════════════════════════════════════════════════════════════

class BookmarkManagerTool:
    name = "bookmarks"
    description = (
        "Browser bookmark manager — import/export HTML, add/remove/search, "
        "organize by domain, check broken links, archive pages, "
        "generate reading lists, bulk screenshots, AI tagging, deduplication"
    )

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _parse_html_bookmarks(html_file: str) -> list:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(Path(html_file).read_text(errors="replace"),
                             "html.parser")
        bookmarks = []
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if href.startswith("http"):
                bookmarks.append({
                    "url": href,
                    "title": a.get_text(strip=True),
                    "add_date": a.get("add_date", ""),
                    "tags": a.get("tags", ""),
                    "folder": ""
                })
        return bookmarks

    # ── Core methods ──────────────────────────────────────────────────────

    @staticmethod
    def import_bookmarks(html_file: str) -> ToolResult:
        try:
            bookmarks = BookmarkManagerTool._parse_html_bookmarks(html_file)
            return ToolResult(True, f"✓ Imported {len(bookmarks)} bookmarks",
                              bookmarks)
        except Exception as e:
            return ToolResult(False, f"✗ import_bookmarks failed: {e}")

    @staticmethod
    def export_bookmarks(bookmarks: list, output_html: str) -> ToolResult:
        try:
            lines = [
                "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
                '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
                "<TITLE>Bookmarks</TITLE>",
                "<H1>Bookmarks</H1>",
                "<DL><p>"
            ]
            for bm in bookmarks:
                title = bm.get("title", bm.get("url", ""))
                url = bm.get("url", "")
                tags = bm.get("tags", "")
                lines.append(
                    f'    <DT><A HREF="{url}" TAGS="{tags}">{title}</A>')
            lines.append("</DL><p>")
            Path(output_html).write_text("\n".join(lines), encoding="utf-8")
            return ToolResult(True, f"✓ Exported {len(bookmarks)} bookmarks to {output_html}")
        except Exception as e:
            return ToolResult(False, f"✗ export_bookmarks failed: {e}")

    @staticmethod
    def add_bookmark(url: str, title: str = "", folder: str = "",
                     tags: str = "", description: str = "") -> ToolResult:
        try:
            store_path = Path.home() / ".npmai_agent" / "bookmarks.json"
            store_path.parent.mkdir(exist_ok=True)
            bms = json.loads(store_path.read_text()) if store_path.exists() else []
            bms.append({
                "url": url, "title": title or url,
                "folder": folder, "tags": tags,
                "description": description,
                "added": datetime.now().isoformat()
            })
            store_path.write_text(json.dumps(bms, indent=2))
            return ToolResult(True, f"✓ Bookmark added: {url}")
        except Exception as e:
            return ToolResult(False, f"✗ add_bookmark failed: {e}")

    @staticmethod
    def remove_bookmark(url: str) -> ToolResult:
        try:
            store_path = Path.home() / ".npmai_agent" / "bookmarks.json"
            if not store_path.exists():
                return ToolResult(False, "No bookmark store found.")
            bms = json.loads(store_path.read_text())
            before = len(bms)
            bms = [b for b in bms if b.get("url") != url]
            store_path.write_text(json.dumps(bms, indent=2))
            return ToolResult(True, f"✓ Removed {before - len(bms)} bookmark(s)")
        except Exception as e:
            return ToolResult(False, f"✗ remove_bookmark failed: {e}")

    @staticmethod
    def search_bookmarks(bookmarks: list = None, query: str = "",
                         tags: str = "", folder: str = "") -> ToolResult:
        try:
            if bookmarks is None:
                store_path = Path.home() / ".npmai_agent" / "bookmarks.json"
                bookmarks = (json.loads(store_path.read_text())
                             if store_path.exists() else [])
            results = []
            for bm in bookmarks:
                if (query.lower() in bm.get("url", "").lower() or
                        query.lower() in bm.get("title", "").lower() or
                        query.lower() in bm.get("description", "").lower()):
                    if tags and tags not in bm.get("tags", ""):
                        continue
                    if folder and folder not in bm.get("folder", ""):
                        continue
                    results.append(bm)
            return ToolResult(True, f"✓ {len(results)} matches", results)
        except Exception as e:
            return ToolResult(False, f"✗ search_bookmarks failed: {e}")

    @staticmethod
    def organize_by_domain(bookmarks: list) -> ToolResult:
        try:
            from urllib.parse import urlparse
            organized: dict = {}
            for bm in bookmarks:
                try:
                    domain = urlparse(bm.get("url", "")).netloc
                    domain = domain.replace("www.", "")
                    organized.setdefault(domain, []).append(bm)
                except Exception:
                    organized.setdefault("other", []).append(bm)
            return ToolResult(True,
                              f"✓ Organized into {len(organized)} domains",
                              organized)
        except Exception as e:
            return ToolResult(False, f"✗ organize_by_domain failed: {e}")

    @staticmethod
    def check_broken_links(bookmarks: list, timeout: int = 10) -> ToolResult:
        try:
            import requests
            broken = []
            ok_count = 0
            for bm in bookmarks:
                url = bm.get("url", "")
                try:
                    resp = requests.head(url, timeout=timeout,
                                        allow_redirects=True,
                                        headers={"User-Agent": "Mozilla/5.0"})
                    if resp.status_code >= 400:
                        broken.append({**bm,
                                       "status": resp.status_code})
                    else:
                        ok_count += 1
                except Exception as ex:
                    broken.append({**bm, "error": str(ex)})
            return ToolResult(True,
                              f"✓ {ok_count} OK, {len(broken)} broken",
                              broken)
        except Exception as e:
            return ToolResult(False, f"✗ check_broken_links failed: {e}")

    @staticmethod
    def archive_page(url: str, output_folder: str) -> ToolResult:
        try:
            from playwright.sync_api import sync_playwright
            out = Path(output_folder)
            out.mkdir(parents=True, exist_ok=True)
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', url)[:80]
            html_path = out / f"{safe_name}.html"
            with sync_playwright() as pw:
                b = pw.chromium.launch(headless=True)
                pg = b.new_page()
                pg.goto(url, timeout=30000,
                        wait_until="networkidle")
                html_path.write_text(pg.content(), encoding="utf-8")
                pg.screenshot(path=str(out / f"{safe_name}.png"),
                              full_page=True)
                b.close()
            return ToolResult(True, f"✓ Archived to {html_path}")
        except Exception as e:
            return ToolResult(False, f"✗ archive_page failed: {e}")

    @staticmethod
    def generate_reading_list(urls: list, output_md: str) -> ToolResult:
        try:
            import requests
            from bs4 import BeautifulSoup
            lines = ["# Reading List\n",
                     f"_Generated: {datetime.now().strftime('%Y-%m-%d')}_\n"]
            for i, url in enumerate(urls, 1):
                try:
                    resp = requests.get(url,
                                        headers={"User-Agent": "Mozilla/5.0"},
                                        timeout=10)
                    soup = BeautifulSoup(resp.text, "html.parser")
                    title = soup.title.string.strip() if soup.title else url
                    desc_tag = soup.find("meta", attrs={"name": "description"})
                    desc = (desc_tag.get("content", "")[:200]
                            if desc_tag else "")
                    lines.append(f"\n## {i}. [{title}]({url})\n")
                    if desc:
                        lines.append(f"> {desc}\n")
                except Exception:
                    lines.append(f"\n## {i}. [{url}]({url})\n")
            Path(output_md).write_text("\n".join(lines), encoding="utf-8")
            return ToolResult(True, f"✓ Reading list saved to {output_md}")
        except Exception as e:
            return ToolResult(False, f"✗ generate_reading_list failed: {e}")

    @staticmethod
    def bulk_screenshot(bookmarks: list, output_folder: str) -> ToolResult:
        try:
            from playwright.sync_api import sync_playwright
            out = Path(output_folder)
            out.mkdir(parents=True, exist_ok=True)
            saved = 0
            with sync_playwright() as pw:
                b = pw.chromium.launch(headless=True)
                pg = b.new_page()
                for bm in bookmarks:
                    url = bm.get("url", "")
                    if not url:
                        continue
                    safe = re.sub(r'[^a-zA-Z0-9_-]', '_', url)[:60]
                    try:
                        pg.goto(url, timeout=15000,
                                wait_until="domcontentloaded")
                        pg.screenshot(path=str(out / f"{safe}.png"),
                                      full_page=False)
                        saved += 1
                    except Exception:
                        pass
                b.close()
            return ToolResult(True, f"✓ Saved {saved} screenshots to {output_folder}")
        except Exception as e:
            return ToolResult(False, f"✗ bulk_screenshot failed: {e}")

    @staticmethod
    def tag_with_ai(bookmarks: list, model: str = "mistral:7b") -> ToolResult:
        """Use local Ollama to auto-tag bookmarks based on title+URL."""
        try:
            import requests
            tagged = []
            for bm in bookmarks:
                url = bm.get("url", "")
                title = bm.get("title", url)
                try:
                    resp = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": model,
                            "prompt": (
                                f"Suggest 3-5 short tags for this bookmark. "
                                f"Reply ONLY with comma-separated tags, nothing else.\n"
                                f"Title: {title}\nURL: {url}"
                            ),
                            "stream": False
                        },
                        timeout=30
                    )
                    tags = resp.json().get("response", "").strip()
                    tagged.append({**bm, "ai_tags": tags})
                except Exception:
                    tagged.append(bm)
            return ToolResult(True, f"✓ Tagged {len(tagged)} bookmarks", tagged)
        except Exception as e:
            return ToolResult(False, f"✗ tag_with_ai failed: {e}")

    @staticmethod
    def deduplicate(bookmarks: list) -> ToolResult:
        try:
            seen: dict = {}
            dupes = 0
            for bm in bookmarks:
                url = bm.get("url", "").rstrip("/").lower()
                if url not in seen:
                    seen[url] = bm
                else:
                    dupes += 1
            unique = list(seen.values())
            return ToolResult(True,
                              f"✓ {len(unique)} unique, {dupes} removed",
                              unique)
        except Exception as e:
            return ToolResult(False, f"✗ deduplicate failed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 10. TimeTrackingTool
# ═════════════════════════════════════════════════════════════════════════════

class TimeTrackingTool:
    name = "time_tracking"
    description = (
        "Time and productivity tracking — local SQLite timer, Toggl + Clockify "
        "integration, timesheets, billing, and invoice export"
    )

    _DB = Path.home() / ".npmai_agent" / "time_tracker.db"

    # ── Database init ─────────────────────────────────────────────────────

    @staticmethod
    def _conn() -> sqlite3.Connection:
        TimeTrackingTool._DB.parent.mkdir(exist_ok=True)
        conn = sqlite3.connect(str(TimeTrackingTool._DB))
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                project  TEXT NOT NULL,
                task     TEXT,
                description TEXT,
                start    TEXT NOT NULL,
                end      TEXT,
                duration INTEGER,
                source   TEXT DEFAULT 'local'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS current_timer (
                id      INTEGER PRIMARY KEY,
                project TEXT,
                task    TEXT,
                description TEXT,
                start   TEXT,
                paused  INTEGER DEFAULT 0,
                pause_start TEXT
            )
        """)
        conn.commit()
        return conn

    # ── Local timer ───────────────────────────────────────────────────────

    @staticmethod
    def start_timer(project: str, task: str = "",
                    description: str = "") -> ToolResult:
        try:
            conn = TimeTrackingTool._conn()
            conn.execute("DELETE FROM current_timer")
            now = datetime.now().isoformat()
            conn.execute(
                "INSERT INTO current_timer(project,task,description,start) "
                "VALUES(?,?,?,?)",
                (project, task, description, now))
            conn.commit()
            return ToolResult(True,
                              f"✓ Timer started: {project}/{task} at {now}")
        except Exception as e:
            return ToolResult(False, f"✗ start_timer failed: {e}")

    @staticmethod
    def stop_timer() -> ToolResult:
        try:
            conn = TimeTrackingTool._conn()
            row = conn.execute(
                "SELECT * FROM current_timer LIMIT 1").fetchone()
            if not row:
                return ToolResult(False, "No active timer.")
            now = datetime.now()
            start = datetime.fromisoformat(row["start"])
            duration_secs = int((now - start).total_seconds())
            conn.execute(
                "INSERT INTO entries(project,task,description,start,end,duration) "
                "VALUES(?,?,?,?,?,?)",
                (row["project"], row["task"], row["description"],
                 row["start"], now.isoformat(), duration_secs))
            conn.execute("DELETE FROM current_timer")
            conn.commit()
            mins = duration_secs // 60
            return ToolResult(True,
                              f"✓ Timer stopped: {row['project']} — {mins} min",
                              {"duration_seconds": duration_secs,
                               "duration_minutes": mins})
        except Exception as e:
            return ToolResult(False, f"✗ stop_timer failed: {e}")

    @staticmethod
    def pause_timer() -> ToolResult:
        try:
            conn = TimeTrackingTool._conn()
            row = conn.execute(
                "SELECT * FROM current_timer LIMIT 1").fetchone()
            if not row:
                return ToolResult(False, "No active timer.")
            if row["paused"]:
                # resume
                paused_secs = int(
                    (datetime.now() -
                     datetime.fromisoformat(row["pause_start"])
                     ).total_seconds())
                # extend start by paused duration to not count it
                new_start = (datetime.fromisoformat(row["start"]) +
                             timedelta(seconds=paused_secs)).isoformat()
                conn.execute(
                    "UPDATE current_timer SET paused=0, pause_start=NULL, start=?",
                    (new_start,))
                conn.commit()
                return ToolResult(True, "✓ Timer resumed")
            else:
                conn.execute(
                    "UPDATE current_timer SET paused=1, pause_start=?",
                    (datetime.now().isoformat(),))
                conn.commit()
                return ToolResult(True, "✓ Timer paused")
        except Exception as e:
            return ToolResult(False, f"✗ pause_timer failed: {e}")

    @staticmethod
    def get_current_timer() -> ToolResult:
        try:
            conn = TimeTrackingTool._conn()
            row = conn.execute(
                "SELECT * FROM current_timer LIMIT 1").fetchone()
            if not row:
                return ToolResult(True, "No active timer", None)
            elapsed = int(
                (datetime.now() -
                 datetime.fromisoformat(row["start"])).total_seconds())
            data = {k: row[k] for k in row.keys()}
            data["elapsed_seconds"] = elapsed
            data["elapsed_minutes"] = elapsed // 60
            return ToolResult(True,
                              f"✓ Running: {row['project']} — {elapsed//60} min",
                              data)
        except Exception as e:
            return ToolResult(False, f"✗ get_current_timer failed: {e}")

    @staticmethod
    def list_time_entries(date_from: str = None, date_to: str = None,
                          project: str = None) -> ToolResult:
        try:
            conn = TimeTrackingTool._conn()
            q = "SELECT * FROM entries WHERE 1=1"
            params: list = []
            if date_from:
                q += " AND start >= ?"
                params.append(date_from)
            if date_to:
                q += " AND start <= ?"
                params.append(date_to + "T23:59:59")
            if project:
                q += " AND project LIKE ?"
                params.append(f"%{project}%")
            q += " ORDER BY start DESC"
            rows = conn.execute(q, params).fetchall()
            entries = [dict(r) for r in rows]
            return ToolResult(True, f"✓ {len(entries)} entries", entries)
        except Exception as e:
            return ToolResult(False, f"✗ list_time_entries failed: {e}")

    @staticmethod
    def add_manual_entry(project: str, task: str, description: str,
                         start: str, end: str) -> ToolResult:
        try:
            conn = TimeTrackingTool._conn()
            s = datetime.fromisoformat(start)
            e = datetime.fromisoformat(end)
            duration = int((e - s).total_seconds())
            conn.execute(
                "INSERT INTO entries(project,task,description,start,end,duration) "
                "VALUES(?,?,?,?,?,?)",
                (project, task, description, start, end, duration))
            conn.commit()
            return ToolResult(True,
                              f"✓ Entry added: {project} {duration//60} min")
        except Exception as e:
            return ToolResult(False, f"✗ add_manual_entry failed: {e}")

    @staticmethod
    def delete_entry(entry_id: int) -> ToolResult:
        try:
            conn = TimeTrackingTool._conn()
            conn.execute("DELETE FROM entries WHERE id=?", (entry_id,))
            conn.commit()
            return ToolResult(True, f"✓ Entry {entry_id} deleted")
        except Exception as e:
            return ToolResult(False, f"✗ delete_entry failed: {e}")

    @staticmethod
    def generate_timesheet(date_from: str, date_to: str,
                           group_by: str = "project",
                           output: str = None) -> ToolResult:
        try:
            result = TimeTrackingTool.list_time_entries(date_from, date_to)
            if not result.success:
                return result
            entries = result.data or []
            # group
            groups: dict = {}
            for e in entries:
                key = e.get(group_by, "unknown")
                groups.setdefault(key, []).append(e)

            lines = [f"# Timesheet: {date_from} → {date_to}\n"]
            total_secs = 0
            for key, grp in sorted(groups.items()):
                secs = sum(e.get("duration", 0) for e in grp)
                total_secs += secs
                h, m = secs // 3600, (secs % 3600) // 60
                lines.append(f"\n## {key}  ({h}h {m}m)")
                for e in grp:
                    d = e.get("duration", 0)
                    lines.append(
                        f"  - {e.get('start','')[:16]}  "
                        f"{e.get('task','')} — {d//60} min  "
                        f"{e.get('description','')}")

            th, tm = total_secs // 3600, (total_secs % 3600) // 60
            lines.append(f"\n**Total: {th}h {tm}m**")
            text = "\n".join(lines)
            if output:
                Path(output).write_text(text, encoding="utf-8")
            return ToolResult(True,
                              f"✓ Timesheet: {th}h {tm}m total",
                              {"text": text,
                               "total_seconds": total_secs})
        except Exception as e:
            return ToolResult(False, f"✗ generate_timesheet failed: {e}")

    @staticmethod
    def get_project_summary(project: str,
                            date_range: tuple = None) -> ToolResult:
        try:
            df = date_range[0] if date_range else None
            dt = date_range[1] if date_range else None
            result = TimeTrackingTool.list_time_entries(df, dt, project)
            if not result.success:
                return result
            entries = result.data or []
            total = sum(e.get("duration", 0) for e in entries)
            tasks: dict = {}
            for e in entries:
                t = e.get("task", "general")
                tasks[t] = tasks.get(t, 0) + e.get("duration", 0)
            summary = {
                "project": project,
                "total_seconds": total,
                "total_hours": round(total / 3600, 2),
                "entry_count": len(entries),
                "by_task": {k: {"seconds": v,
                                "hours": round(v / 3600, 2)}
                            for k, v in tasks.items()}
            }
            return ToolResult(True,
                              f"✓ {project}: {round(total/3600,2)}h",
                              summary)
        except Exception as e:
            return ToolResult(False, f"✗ get_project_summary failed: {e}")

    @staticmethod
    def calculate_billing(date_from: str, date_to: str,
                          hourly_rate: float, project: str = None) -> ToolResult:
        try:
            result = TimeTrackingTool.list_time_entries(
                date_from, date_to, project)
            if not result.success:
                return result
            entries = result.data or []
            total_secs = sum(e.get("duration", 0) for e in entries)
            hours = total_secs / 3600
            amount = round(hours * hourly_rate, 2)
            return ToolResult(True,
                              f"✓ {round(hours,2)}h × ${hourly_rate}/h = ${amount}",
                              {"hours": round(hours, 2),
                               "rate": hourly_rate,
                               "amount": amount,
                               "currency": "USD"})
        except Exception as e:
            return ToolResult(False, f"✗ calculate_billing failed: {e}")

    @staticmethod
    def export_to_invoice(date_from: str, date_to: str, client: str,
                          rate: float, output: str) -> ToolResult:
        try:
            billing = TimeTrackingTool.calculate_billing(
                date_from, date_to, rate)
            if not billing.success:
                return billing
            bd = billing.data
            timesheet = TimeTrackingTool.generate_timesheet(date_from, date_to)
            ts_text = timesheet.data.get("text", "") if timesheet.data else ""
            invoice = f"""# INVOICE

**To:** {client}
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Period:** {date_from} — {date_to}

---

## Summary

| Hours | Rate | Amount |
|-------|------|--------|
| {bd['hours']}h | ${bd['rate']}/h | ${bd['amount']} |

---

## Detail

{ts_text}

---

**TOTAL DUE: ${bd['amount']} USD**
"""
            Path(output).write_text(invoice, encoding="utf-8")
            return ToolResult(True,
                              f"✓ Invoice saved to {output} — ${bd['amount']}",
                              bd)
        except Exception as e:
            return ToolResult(False, f"✗ export_to_invoice failed: {e}")

    # ── Toggl ─────────────────────────────────────────────────────────────

    @staticmethod
    def connect_toggl(api_token: str) -> ToolResult:
        try:
            CredStore.save("toggl", {"api_token": api_token})
            return ToolResult(True, "✓ Toggl API token saved")
        except Exception as e:
            return ToolResult(False, f"✗ connect_toggl failed: {e}")

    @staticmethod
    def toggl_list_projects(cred_key: str = "toggl") -> ToolResult:
        try:
            import requests
            token = CredStore.load(cred_key).get("api_token", "")
            if not token:
                return ToolResult(False, "No Toggl token.")
            # get workspace id first
            me = requests.get(
                "https://api.track.toggl.com/api/v9/me",
                auth=(token, "api_token"), timeout=10).json()
            wid = me.get("default_workspace_id")
            resp = requests.get(
                f"https://api.track.toggl.com/api/v9/workspaces/{wid}/projects",
                auth=(token, "api_token"), timeout=10)
            resp.raise_for_status()
            projects = resp.json()
            return ToolResult(True, f"✓ {len(projects)} Toggl projects",
                              projects)
        except Exception as e:
            return ToolResult(False, f"✗ toggl_list_projects failed: {e}")

    @staticmethod
    def toggl_start_timer(project_id: int, description: str = "",
                          cred_key: str = "toggl") -> ToolResult:
        try:
            import requests
            token = CredStore.load(cred_key).get("api_token", "")
            me = requests.get(
                "https://api.track.toggl.com/api/v9/me",
                auth=(token, "api_token"), timeout=10).json()
            wid = me.get("default_workspace_id")
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            body = {
                "created_with": "npmai-agent",
                "description": description,
                "project_id": project_id,
                "start": now,
                "duration": -1,
                "workspace_id": wid
            }
            resp = requests.post(
                f"https://api.track.toggl.com/api/v9/workspaces/{wid}/time_entries",
                auth=(token, "api_token"), json=body, timeout=10)
            resp.raise_for_status()
            entry = resp.json()
            return ToolResult(True, f"✓ Toggl timer started: {entry.get('id')}", entry)
        except Exception as e:
            return ToolResult(False, f"✗ toggl_start_timer failed: {e}")

    # ── Clockify ──────────────────────────────────────────────────────────

    @staticmethod
    def connect_clockify(api_token: str) -> ToolResult:
        try:
            CredStore.save("clockify", {"api_token": api_token})
            return ToolResult(True, "✓ Clockify API token saved")
        except Exception as e:
            return ToolResult(False, f"✗ connect_clockify failed: {e}")

    @staticmethod
    def clockify_list_projects(workspace_id: str = None,
                                cred_key: str = "clockify") -> ToolResult:
        try:
            import requests
            token = CredStore.load(cred_key).get("api_token", "")
            if not token:
                return ToolResult(False, "No Clockify token.")
            headers = {"X-Api-Key": token}
            if not workspace_id:
                user = requests.get(
                    "https://api.clockify.me/api/v1/user",
                    headers=headers, timeout=10).json()
                workspace_id = user.get("defaultWorkspace", "")
            resp = requests.get(
                f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/projects",
                headers=headers, timeout=10)
            resp.raise_for_status()
            projects = resp.json()
            return ToolResult(True, f"✓ {len(projects)} Clockify projects",
                              projects)
        except Exception as e:
            return ToolResult(False, f"✗ clockify_list_projects failed: {e}")

    @staticmethod
    def clockify_time_entry(workspace_id: str, project_id: str,
                             description: str,
                             start: str, end: str,
                             cred_key: str = "clockify") -> ToolResult:
        try:
            import requests
            token = CredStore.load(cred_key).get("api_token", "")
            headers = {"X-Api-Key": token,
                       "Content-Type": "application/json"}

            def _fmt(dt_str: str) -> str:
                return (datetime.fromisoformat(dt_str)
                        .strftime("%Y-%m-%dT%H:%M:%SZ"))

            body = {
                "start": _fmt(start),
                "end": _fmt(end),
                "description": description,
                "projectId": project_id
            }
            resp = requests.post(
                f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/time-entries",
                headers=headers, json=body, timeout=10)
            resp.raise_for_status()
            entry = resp.json()
            return ToolResult(True,
                              f"✓ Clockify entry logged: {entry.get('id')}",
                              entry)
        except Exception as e:
            return ToolResult(False, f"✗ clockify_time_entry failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────────────────────────────────────

PRODUCTIVITY_TOOLS = {
    GoogleWorkspaceTool.name:  GoogleWorkspaceTool,
    NotionAdvancedTool.name:   NotionAdvancedTool,
    LinearTool.name:           LinearTool,
    AsanaTool.name:            AsanaTool,
    TrelloTool.name:           TrelloTool,
    ClickUpTool.name:          ClickUpTool,
    TodoistTool.name:          TodoistTool,
    ObsidianTool.name:         ObsidianTool,
    BookmarkManagerTool.name:  BookmarkManagerTool,
    TimeTrackingTool.name:     TimeTrackingTool,
}

PRODUCTIVITY_TOOLS_SUMMARY = "\n".join(
    f"- {k}: {v.description}"
    for k, v in PRODUCTIVITY_TOOLS.items()
)
