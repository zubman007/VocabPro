"""Course categories with a conservative, read-only adapter for legacy descriptions."""
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from uuid import uuid4, uuid5, NAMESPACE_URL
import pandas as pd
from app.repositories.csv_store import read_document
from app.shared.atomic_bytes import save_bytes
from app.shared.storage import save_csv, file_revision, destination_lock, FileChangedError
from app.shared.messages import UserMessageError

CATEGORY_COLUMN='Category'
COLUMNS=('ID','Name','Description')


def category_key(value):
    return str(value or '').strip().casefold()


def catalog_path(course):
    course=Path(course)
    return course.with_name(course.stem+'_categories.csv')


def validate_catalog(frame):
    if not set(COLUMNS)<=set(frame):raise UserMessageError('Invalid conjugation categories.')
    keys=frame.Name.map(category_key)
    if (frame.ID.eq('').any() or frame.ID.duplicated().any() or keys.eq('').any() or keys.duplicated().any()):
        raise UserMessageError('Invalid conjugation categories.')
    return frame


def load_catalog(course,source):
    """No writes: derive missing definitions only for pre-category source files."""
    frame,revision=read_document(catalog_path(course),optional=True,columns=COLUMNS)
    validate_catalog(frame)
    if CATEGORY_COLUMN not in source:
        known=dict(zip(frame.Name.map(category_key),frame.ID))
        known_ids=set(frame.ID)
        legacy_ids={}
        additions=[]
        for description in source.get('Description',[]):
            name=str(description).split(',',1)[0].strip()
            key=category_key(name)
            identifier=uuid5(NAMESPACE_URL,f'vocabpro:{Path(course).stem}:{key}').hex
            if key and identifier in known_ids:
                # Recover a renamed definition even if the source schema has
                # not been saved yet (including an interrupted first migration).
                legacy_ids[key]=identifier
            elif key and key in known:legacy_ids[key]=known[key]
            elif key:
                row=dict.fromkeys(frame.columns,'')
                row.update(ID=identifier,Name=name)
                additions.append(row);known[key]=identifier;known_ids.add(identifier);legacy_ids[key]=identifier
        if additions:frame=pd.concat([frame,pd.DataFrame(additions)],ignore_index=True)
        frame.attrs['legacy_category_ids']=legacy_ids
    return validate_catalog(frame),revision


def category_ids(source,catalog):
    if CATEGORY_COLUMN in source:
        ids=source[CATEGORY_COLUMN].fillna('').astype(str)
        if set(ids)-set(catalog.ID)-{''}:raise UserMessageError('Invalid conjugation categories.')
        return ids.copy()
    names={**dict(zip(catalog.Name.map(category_key),catalog.ID)),**catalog.attrs.get('legacy_category_ids',{})}
    descriptions=source.get('Description',pd.Series('',index=source.index,dtype=object))
    return descriptions.map(lambda value:names.get(category_key(str(value).split(',',1)[0]),''))


def category_names(source,catalog):
    return category_ids(source,catalog).map(dict(zip(catalog.ID,catalog.Name))).fillna('')


def filter_categories(source,catalog,selected):
    if selected is None:return source.copy()
    wanted={category_key(value) for value in selected}
    selected_ids=set(catalog.loc[catalog.Name.map(category_key).isin(wanted)|catalog.ID.isin(selected),'ID'])
    if '' in wanted:selected_ids.add('')
    return source.loc[category_ids(source,catalog).isin(selected_ids)].copy()


@contextmanager
def save_catalog_with_answers(course,frame,revision):
    """Rollback only our catalog write if the corresponding source save fails."""
    path=catalog_path(course)
    validate_catalog(frame)
    with destination_lock(path):
        original=path.read_bytes() if path.exists() else None
        current=sha256(original).digest() if original is not None else None
        if current!=revision:raise FileChangedError('The course file changed. Reopen the editor before saving.')
        changed=original is None
        if original is not None:
            current_frame,_=read_document(path)
            changed=not frame.equals(current_frame)
        if changed:
            save_csv(frame,path,sep=';',index=False,expected_revision=revision,expect_missing=revision is None)
            written=file_revision(path)
        try:yield
        except BaseException:
            if changed:
                if not path.exists() or file_revision(path)!=written:
                    raise FileChangedError('The course file changed. Reopen the editor before saving.')
                if original is None:path.unlink()
                else:save_bytes(path,original,revision=written)
            raise


def ensure_catalog(course,source):
    frame,revision=load_catalog(course,source)
    with save_catalog_with_answers(course,frame,revision):pass
    return frame


class ConjugationTables:
    """Reconcile spreadsheet edits by stable IDs, preserving histories/hidden forms."""
    def __init__(self,document):
        self.document=document
        self.catalog,self.revision=load_catalog(document.path,document.frame)
        self.aliases=dict(zip(self.catalog.Name.map(category_key),self.catalog.ID))
        document.frame[CATEGORY_COLUMN]=category_ids(document.frame,self.catalog)
        document.initial=document.frame.copy(deep=True)
        self.initial_catalog=self.catalog.copy(deep=True)
        self.fields=(document.language,document.learned_by,CATEGORY_COLUMN,'Description',
                     *(person.id for person in document.config.active))

    @property
    def dirty(self):
        return not self.document.frame.equals(self.document.initial) or not self.catalog.equals(self.initial_catalog)

    def verb_rows(self,query=''):
        frame=self.document.frame.copy()
        frame[CATEGORY_COLUMN]=category_names(frame,self.catalog)
        if query:
            frame=frame.loc[frame[list(self.fields)].apply(
                lambda col:col.astype(str).str.casefold().str.contains(query.casefold(),regex=False)).any(axis=1)]
        return frame[['ID',*self.fields]].values.tolist()

    def apply(self,verb_rows,visible_ids,category_rows):
        """Validate both drafts completely before changing either document."""
        old_catalog=self.catalog.set_index('ID',drop=False)
        category_data=[]
        for row in category_rows:
            row=list(row)+['']*max(0,3-len(row))
            if any(str(v).strip() for v in row[3:]):raise UserMessageError('Too many pasted columns.')
            identifier,name,description=(str(v) for v in row[:3])
            if not identifier and not name.strip() and not description.strip():continue
            if identifier and identifier not in old_catalog.index:raise UserMessageError('Invalid conjugation categories.')
            data=old_catalog.loc[identifier].to_dict() if identifier else dict.fromkeys(self.catalog.columns,'')
            data.update(ID=identifier or uuid4().hex,Name=name.strip(),Description=description)
            category_data.append(data)
        catalog=pd.DataFrame(category_data,columns=self.catalog.columns)
        validate_catalog(catalog)
        names={**{name:identifier for name,identifier in self.aliases.items() if identifier in set(catalog.ID)},
               **dict(zip(catalog.Name.map(category_key),catalog.ID))}
        old_names=dict(zip(self.catalog.ID,self.catalog.Name))
        frame=self.document.frame.copy(deep=True);original=frame.set_index('ID',drop=False)
        seen=set();rows=[]
        for row in verb_rows:
            row=list(row)+['']*max(0,len(self.fields)+1-len(row))
            if any(str(v).strip() for v in row[len(self.fields)+1:]):raise UserMessageError('Too many pasted columns.')
            identifier=str(row[0]);values=dict(zip(self.fields,map(str,row[1:])))
            if not identifier and not any(value.strip() for value in values.values()):continue
            if identifier and (identifier not in visible_ids or identifier in seen):raise UserMessageError('Practice requires unique word IDs')
            if not values[self.document.language].strip():raise UserMessageError('Enter the verb in the learning language.')
            data=original.loc[identifier].to_dict() if identifier else dict.fromkeys(frame.columns,'')
            identifier=identifier or uuid4().hex
            seen.add(identifier)
            for key,value in values.items():
                if key==CATEGORY_COLUMN:
                    name=value.strip();key_name=category_key(name)
                    if not name:value=''
                    elif identifier in original.index and key_name==category_key(old_names.get(data.get(CATEGORY_COLUMN,''),'')):
                        value=data[CATEGORY_COLUMN]
                    elif key_name in names:value=names[key_name]
                    else:
                        value=uuid4().hex;names[key_name]=value
                        item=dict.fromkeys(catalog.columns,'');item.update(ID=value,Name=name)
                        catalog=pd.concat([catalog,pd.DataFrame([item])],ignore_index=True)
                elif value!=data.get(key,''):value=value.strip()
                data[key]=value
            data['ID']=identifier;rows.append(data)
        retained=frame.loc[~frame.ID.isin(visible_ids)]
        updated=pd.concat([retained,pd.DataFrame(rows,columns=frame.columns)],ignore_index=True)
        # Preserve original order; new pasted rows go at the end.
        order={identifier:index for index,identifier in enumerate(frame.ID)}
        positions=[order.get(identifier,len(order)+i) for i,identifier in enumerate(updated.ID)]
        updated=updated.iloc[sorted(range(len(updated)),key=positions.__getitem__)].reset_index(drop=True)
        category_ids(updated,catalog)
        self.catalog=catalog;self.document.frame=updated
        self.aliases.update(dict(zip(catalog.Name.map(category_key),catalog.ID)))

    def save(self):
        with save_catalog_with_answers(self.document.path,self.catalog,self.revision):
            if CATEGORY_COLUMN not in self.document.source_columns:
                original=self.document.path.read_bytes()
                if sha256(original).digest()!=self.document.revision:
                    raise FileChangedError('The course file changed. Reopen the editor before saving.')
                from app.repositories.conjugation import backup_legacy
                backup_legacy(self.document.path,original,suffix='.pre-categories.bak')
            self.document.save()
        self.revision=file_revision(catalog_path(self.document.path))
        self.initial_catalog=self.catalog.copy(deep=True)
