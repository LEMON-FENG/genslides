"""Give notes masters private theme parts when shared with another master.

Changing PresentationML child order can expose PowerPoint loader failures when
a generated notes master and slide master share the same theme part. Clone the
theme bytes and its optional relationships; preserve notes content and styling.
"""
import posixpath
from xml.dom import minidom

REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'


def resolve(part, target):
    return posixpath.normpath(posixpath.join(posixpath.dirname(posixpath.dirname(part)), target)).lstrip('/')


def isolate_notes_themes(data):
    owners = {}
    notes = []
    for name, payload in list(data.items()):
        if not name.endswith('.rels') or not name.startswith(('ppt/slideMasters/_rels/', 'ppt/notesMasters/_rels/')):
            continue
        doc = minidom.parseString(payload)
        for rel in doc.getElementsByTagNameNS(REL, 'Relationship'):
            if not rel.getAttribute('Type').endswith('/theme') or rel.getAttribute('TargetMode') == 'External':
                continue
            target = resolve(name, rel.getAttribute('Target'))
            owners.setdefault(target, []).append(name)
            if name.startswith('ppt/notesMasters/'):
                notes.append((name, doc, rel, target))
    changes = []
    content_types = minidom.parseString(data['[Content_Types].xml'])
    types = {e.getAttribute('PartName').lstrip('/'): e.getAttribute('ContentType')
             for e in content_types.getElementsByTagNameNS(CT, 'Override')}
    for name, doc, rel, target in notes:
        if len(owners[target]) < 2:
            continue
        if target not in data:
            raise ValueError('Notes theme target is missing: '+target)
        folder, number = posixpath.dirname(target), 1
        new_target = posixpath.join(folder, 'themeNotes%d.xml' % number)
        while new_target in data:
            number += 1
            new_target = posixpath.join(folder, 'themeNotes%d.xml' % number)
        data[new_target] = data[target]
        old_rels = posixpath.join(folder, '_rels', posixpath.basename(target)+'.rels')
        if old_rels in data:
            data[posixpath.join(folder, '_rels', posixpath.basename(new_target)+'.rels')] = data[old_rels]
        rel.setAttribute('Target', posixpath.relpath(new_target, posixpath.dirname(posixpath.dirname(name))))
        data[name] = doc.toxml(encoding='UTF-8')
        override = content_types.createElementNS(CT, 'Override')
        override.setAttribute('PartName', '/'+new_target)
        override.setAttribute('ContentType', types.get(target, 'application/vnd.openxmlformats-officedocument.theme+xml'))
        content_types.documentElement.appendChild(override)
        changes.append({'owner': name, 'original_theme': target, 'private_theme': new_target})
    if changes:
        data['[Content_Types].xml'] = content_types.toxml(encoding='UTF-8')
    return changes
