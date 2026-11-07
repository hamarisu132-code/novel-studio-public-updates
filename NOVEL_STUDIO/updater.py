"""NOVEL STUDIO updater. Runs OUTSIDE the versioned application folder.
Explicit opt-in only; fetches public GitHub release via HTTPS, no user data uploaded.
"""
import hashlib, io, json, os, shutil, subprocess, sys, tempfile, time, urllib.request, zipfile
from pathlib import Path

REPO = 'hamarisu132-code/novel-studio-public-updates'
API = f'https://api.github.com/repos/{REPO}/releases/latest'
ASSET = 'NOVEL_STUDIO_Windows.zip'
MAX_DOWNLOAD = 350 * 1024 * 1024
MAX_UNPACKED = 900 * 1024 * 1024

def base_dir():
    return Path(sys.executable if getattr(sys, 'frozen', False) else __file__).resolve().parent

def get_json(url):
    req = urllib.request.Request(url, headers={'Accept':'application/vnd.github+json','User-Agent':'NOVEL-STUDIO-Updater'})
    with urllib.request.urlopen(req, timeout=20) as r:
        if not r.geturl().startswith('https://api.github.com/'):
            raise RuntimeError('Unexpected API redirect')
        return json.load(r)

def version(tag):
    s = tag.lstrip('v').split('-')[0].split('.')
    if len(s) != 3 or any(not p.isdigit() for p in s):
        raise ValueError('Invalid version: '+tag)
    return tuple(map(int, s))

def latest():
    release = get_json(API)
    tag = release['tag_name']
    version(tag)
    asset = next((a for a in release.get('assets',[]) if a.get('name') == ASSET), None)
    if not asset:
        raise RuntimeError('Release has no '+ASSET+' asset. Nothing was changed.')
    return tag, asset

def download(asset):
    url = asset['browser_download_url']
    if not url.startswith(f'https://github.com/{REPO}/releases/download/'):
        raise RuntimeError('Unexpected download source')
    req = urllib.request.Request(url, headers={'User-Agent':'NOVEL-STUDIO-Updater'})
    with urllib.request.urlopen(req, timeout=60) as r:
        if not r.geturl().startswith('https://'):
            raise RuntimeError('Unsafe redirect')
        chunks=[]; size=0
        while True:
            part=r.read(1024*1024)
            if not part: break
            size += len(part)
            if size > MAX_DOWNLOAD: raise RuntimeError('Download exceeds limit')
            chunks.append(part)
    data=b''.join(chunks)
    # GitHub computes SHA256 for release assets; require it to be present.
    digest=asset.get('digest','')
    if not digest.startswith('sha256:') or len(digest)!=71:
        raise RuntimeError('GitHub asset SHA256 digest is missing')
    if hashlib.sha256(data).hexdigest()!=digest[7:].lower():
        raise RuntimeError('Downloaded asset SHA256 mismatch')
    return data

def unpack(data, stage):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        entries=z.infolist()
        if len(entries)>4000 or sum(i.file_size for i in entries)>MAX_UNPACKED:
            raise RuntimeError('Archive too large')
        for i in entries:
            p=Path(i.filename.replace('\\','/'))
            if p.is_absolute() or '..' in p.parts or ':' in i.filename or (i.external_attr>>16)&0o170000==0o120000:
                raise RuntimeError('Unsafe archive entry')
            if p.parts and p.parts[0].lower() in ('data','userdata'):
                raise RuntimeError('Release contains user data folder')
            if p.name.lower() in ('novel_studio.db','update_config.json'):
                raise RuntimeError('Release contains protected data/config')
        z.extractall(stage)
    if not (stage/'NOVEL_STUDIO.exe').is_file() or not (stage/'_internal').is_dir():
        raise RuntimeError('Invalid app package layout')

def app_version(app):
    file=app/'version.json'
    if not file.exists(): file=app/'_internal'/'version.json'
    if not file.exists(): return '0.4.0'
    return json.loads(file.read_text(encoding='utf-8'))['version']

def install(app, tag, data):
    parent=app.parent
    with tempfile.TemporaryDirectory(prefix='novel-stage-', dir=parent) as temp:
        stage=Path(temp)/'app'; stage.mkdir()
        unpack(data,stage)
        package_version=app_version(stage)
        if version(package_version)!=version(tag):
            raise RuntimeError('Release tag does not match package version')
        old=parent/'NOVEL_STUDIO.previous'
        if old.exists():
            # Preserve rollback from earlier update; never delete it silently.
            raise RuntimeError('Previous backup exists. Please move it elsewhere before updating: '+str(old))
        # Application must be closed. Rename will fail if Windows has locked files.
        if app.exists(): os.replace(app,old)
        try:
            os.replace(stage,app)
        except Exception:
            if old.exists() and not app.exists(): os.replace(old,app)
            raise
        print('Update installed. Old app kept in:',old)

def main():
    home=base_dir()
    app=home/'NOVEL_STUDIO'
    if not (app/'NOVEL_STUDIO.exe').is_file():
        print('Application not installed beside launcher:',app); return
    current=app_version(app)
    print('Current version:',current)
    print('Checking public GitHub release (no manuscript data sent)...')
    tag,asset=latest()
    print('Latest release:',tag)
    if version(tag)<=version(current):
        print('Already up to date.'); return
    if input('Download and apply this update? [y/N] ').strip().lower()!='y': return
    print('Downloading verified release...')
    data=download(asset)
    print('Close NOVEL STUDIO before applying the update.')
    if input('Is NOVEL STUDIO closed? Apply now? [y/N] ').strip().lower()!='y': return
    install(app,tag,data)
    print('Done. You can now start NOVEL_STUDIO.exe from the launcher folder.')

if __name__=='__main__':
    try: main()
    except Exception as exc: print('Update cancelled:',str(exc))
    input('Press Enter to close...')
