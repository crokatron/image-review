"""Scoped release: preserve the exact live release, adding only the owner reviewer."""
import hashlib,io,json,tarfile,time
from pathlib import Path

BASE=Path(__file__).resolve().parent

def verified_archive(path):
    with tarfile.open(path,'r:gz') as archive:
        rows=archive.getmembers()
        assert all(m.isfile() and not m.name.startswith('/') and '\\' not in m.name and '..' not in Path(m.name).parts for m in rows)
        assert len({m.name for m in rows})==len(rows)
        files={m.name:archive.extractfile(m).read() for m in rows}
    manifest=json.loads(files.pop('release.json'))
    assert manifest['files']=={n:hashlib.sha256(b).hexdigest() for n,b in sorted(files.items())}
    return files,manifest

def integrate(server,module):
    if '# BEGIN IMAGE REVIEW MODULE' in server:
        start=server.index('# BEGIN IMAGE REVIEW MODULE');end=server.index('# END IMAGE REVIEW MODULE',start)+len('# END IMAGE REVIEW MODULE')
        server=server[:start]+'# BEGIN IMAGE REVIEW MODULE\n'+module+'\n# END IMAGE REVIEW MODULE'+server[end:]
    else:
        needle='ROOT = Path(__file__).resolve().parent'
        assert server.count(needle)==1
        server=server.replace(needle,'# BEGIN IMAGE REVIEW MODULE\n'+module+'\n# END IMAGE REVIEW MODULE\n\n'+needle)
        needle='QR_BACKUPS = QRBackups(DATA)'
        assert server.count(needle)==1
        server=server.replace(needle,needle+'\nIMAGE_REVIEW = ImageReview(DATA)')
        needle="        if not self.authorize(): return\n        if p.startswith('/api/admin/qr-backups'):"
        assert server.count(needle)==1
        server=server.replace(needle,"        if not self.authorize(): return\n        if p.startswith('/image-review/api/'): return image_review_request(self, IMAGE_REVIEW)\n        if p == '/image-review':\n            self.send_response(308); self.send_header('Location','/image-review/'); self.end_headers(); return\n        if p.startswith('/api/admin/qr-backups'):")
        needle="        if not self.authorize(): return\n        if self.path.startswith('/api/admin/qr-backups'):"
        assert server.count(needle)==1
        server=server.replace(needle,"        if not self.authorize(): return\n        if self.path.startswith('/image-review/api/'): return image_review_request(self, IMAGE_REVIEW)\n        if self.path.startswith('/api/admin/qr-backups'):")
    compile(server,'server.py','exec')
    return server

def build(base,current):
    files,previous=verified_archive(base)
    assert previous['id']==current,'Base release does not match live release'
    source=BASE.parent/'host/image_review.py'
    if not source.exists():source=BASE/'source/image_review.py'
    server=integrate(files['server.py'].decode('utf-8-sig'),source.read_text(encoding='utf-8'))
    files['server.py']=server.encode()
    index=files['public/index.html'].decode('utf-8-sig')
    entry={"id":"image-review","name":"Image Review","tag":"Photos & organisation","category":"tools","owner":True,
      "description":"Review one image at a time. Swipe or tap Meme and Not meme, with your choices saved on the NAS.",
      "chips":["Swipe review","Undo","Saved decisions"],"storage":"Owner only · Private previews and decisions on the NAS",
      "features":["Start with the 5,174 borderline images or choose another likelihood band.","Swipe right for Meme, left for Not meme, or skip for later.","Undo choices and resume across your devices.","Export decisions and their reversible history. Original images stay untouched."],
      "steps":["Open the borderline review queue.","Swipe or tap a decision. Changes save as you go.","Return to skipped images or export your decisions."],
      "phone":"Large image cards and touch controls work in your phone browser. Pinch the enlarged preview to read small text."}
    if '"id":"image-review"' not in index and '"id": "image-review"' not in index:
        needle='const projects=[';assert index.count(needle)==1
        index=index.replace(needle,needle+'\n '+json.dumps(entry,ensure_ascii=True)+',')
    files['public/index.html']=index.encode()
    for name in ('index.html','style.css','app.js'):files['public/image-review/'+name]=(BASE/'public'/name).read_bytes()
    allowed={'server.py','public/index.html',*(f'public/image-review/{name}' for name in ('index.html','style.css','app.js'))}
    assert all(files[n]==b for n,b in verified_archive(base)[0].items() if n not in allowed)
    assert not any(n.startswith(('data/','secrets/')) or n.endswith(('.key','.sqlite3','.jpg')) for n in files)
    manifest={'id':time.strftime('%Y-%m-%d %H:%M:%S UTC',time.gmtime()),'files':{n:hashlib.sha256(b).hexdigest() for n,b in sorted(files.items())}}
    out=BASE/'release.tar.gz'
    with tarfile.open(out,'w:gz') as archive:
        for name,content in sorted({**files,'release.json':json.dumps(manifest,indent=2).encode()}.items()):
            member=tarfile.TarInfo(name);member.size=len(content);member.mode=0o644;archive.addfile(member,io.BytesIO(content))
    (BASE/'manifest.json').write_text(json.dumps(manifest,indent=2))
    (BASE/'integrated-server.py').write_text(server,encoding='utf-8')
    print('Scoped release built:',manifest['id'],'; other 86 files preserved byte for byte')
    return out,manifest

if __name__=='__main__':build(BASE/'base-release.tar.gz',json.loads((BASE/'base-manifest.json').read_text())['id'])
