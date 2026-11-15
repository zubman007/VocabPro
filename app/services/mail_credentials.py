"""SMTP sender stored in the current user's Windows Credential Manager."""
import ctypes
from ctypes import wintypes
import os

TARGET='VocabPro/SMTP'


class _Credential(ctypes.Structure):
    _fields_=[('Flags',wintypes.DWORD),('Type',wintypes.DWORD),
        ('TargetName',wintypes.LPWSTR),('Comment',wintypes.LPWSTR),
        ('LastWritten',wintypes.FILETIME),('CredentialBlobSize',wintypes.DWORD),
        ('CredentialBlob',ctypes.POINTER(ctypes.c_ubyte)),('Persist',wintypes.DWORD),
        ('AttributeCount',wintypes.DWORD),('Attributes',ctypes.c_void_p),
        ('TargetAlias',wintypes.LPWSTR),('UserName',wintypes.LPWSTR)]


def _api():
    if os.name!='nt':raise OSError('Windows Credential Manager is unavailable.')
    api=ctypes.WinDLL('Advapi32.dll',use_last_error=True)
    api.CredReadW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.POINTER(ctypes.POINTER(_Credential))]
    api.CredReadW.restype=wintypes.BOOL
    api.CredWriteW.argtypes=[ctypes.POINTER(_Credential),wintypes.DWORD]
    api.CredWriteW.restype=wintypes.BOOL
    api.CredFree.argtypes=[ctypes.c_void_p]
    api.CredFree.restype=None
    return api


def load_credentials():
    return _read_credentials(_api())


def _read_credentials(api):
    pointer=ctypes.POINTER(_Credential)()
    if not api.CredReadW(TARGET,1,0,ctypes.byref(pointer)):
        if ctypes.get_last_error()==1168:return None
        raise OSError('Could not read the sending account from Windows Credential Manager.')
    try:
        item=pointer.contents
        password=ctypes.string_at(item.CredentialBlob,item.CredentialBlobSize).decode('utf-8')
        return (item.UserName,password) if item.UserName and password else None
    finally:api.CredFree(pointer)


def save_credentials(username,password):
    return _write_credentials(_api(),username,password)


def _write_credentials(api,username,password):
    username=username.strip()
    if '@' not in username or any(c.isspace() or c=='\0' for c in username):
        raise ValueError('Enter a valid email address.')
    if not password or '\0' in password:raise ValueError('Enter the SMTP password.')
    encoded=password.encode('utf-8')
    if len(encoded)>2560:raise ValueError('The SMTP password is too long.')
    buffer=(ctypes.c_ubyte*len(encoded)).from_buffer_copy(encoded)
    item=_Credential(Type=1,TargetName=TARGET,UserName=username,Persist=2,
        CredentialBlobSize=len(encoded),CredentialBlob=ctypes.cast(buffer,ctypes.POINTER(ctypes.c_ubyte)))
    try:
        if not api.CredWriteW(ctypes.byref(item),0):
            raise OSError('Could not save the sending account in Windows Credential Manager.')
    finally:ctypes.memset(buffer,0,len(encoded))
