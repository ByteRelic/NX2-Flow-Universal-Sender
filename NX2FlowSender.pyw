import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket, struct, pathlib, threading, queue, time, zlib, json, os

config_path = pathlib.Path(os.environ.get("LOCALAPPDATA", str(pathlib.Path.home()))) / "NX2FlowSender" / "settings.json"
def load_host():
    try:
        value = json.loads(config_path.read_text(encoding="utf-8")).get("host", "")
        return value if isinstance(value, str) else ""
    except (OSError, ValueError, AttributeError):
        return ""
def save_host(value):
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps({"host": value}), encoding="utf-8")
    except OSError:
        pass

root=tk.Tk(); root.title('NX2 Flow Universal Sender v0.1.0-beta'); root.geometry('760x550'); root.configure(bg='#17191f')
style=ttk.Style(); style.theme_use('clam'); style.configure('.',background='#252832',foreground='#eeeeee',fieldbackground='#343845'); style.configure('TButton',padding=8); style.configure('TProgressbar',background='#438af5',troughcolor='#343845'); style.map('TButton',background=[('active','#404655')]); style.configure('Treeview',background='#20232b',fieldbackground='#20232b',foreground='white',rowheight=28)
frame=ttk.Frame(root,padding=20); frame.pack(fill='both',expand=True)
ttk.Label(frame,text='NX2 FLOW / UNIVERSAL SENDER',font=('Segoe UI',19,'bold')).pack(anchor='w',pady=(0,15))
bar=ttk.Frame(frame); bar.pack(fill='x'); host=tk.StringVar(value=load_host()); port=tk.StringVar(value='28302')
ttk.Label(bar,text='Console IP').pack(side='left'); ttk.Entry(bar,textvariable=host,width=20).pack(side='left',padx=8); ttk.Label(bar,text='Port').pack(side='left'); ttk.Entry(bar,textvariable=port,width=8).pack(side='left',padx=8)
files={}; tree=ttk.Treeview(frame,columns=('size','state'),show='tree headings',height=8); tree.heading('#0',text='File'); tree.heading('size',text='Size (GiB)'); tree.heading('state',text='Status'); tree.column('#0',width=350); tree.column('size',width=100); tree.column('state',width=160); tree.pack(fill='both',expand=True,pady=12)
events=queue.Queue(); stop=threading.Event(); active=False

def add():
    for name in filedialog.askopenfilenames(filetypes=[('NUP files','*.nup'),('All files','*.*')]):
        p=pathlib.Path(name)
        if name not in files.values():
            i=tree.insert('', 'end',text=p.name,values=(f'{p.stat().st_size/2**30:.2f}','Ready')); files[i]=name

def remove():
    for i in tree.selection(): files.pop(i,None); tree.delete(i)

def recv(s,n):
    b=bytearray()
    while len(b)<n:
        x=s.recv(n-len(b))
        if not x: raise ConnectionError('Connection closed')
        b.extend(x)
    return bytes(b)

def check(s):
    if recv(s,1)[0]:
        n=struct.unpack('<H',recv(s,2))[0]; raise RuntimeError(recv(s,n).decode(errors='replace'))

def worker(h,p,items):
    try:
        for i,name in items:
            if stop.is_set(): break
            f=pathlib.Path(name); size=f.stat().st_size; dest=('/nx2-flow/games/'+f.name).encode('utf-8'); sent=crc=0
            events.put(('state',i,'Connecting'))
            with socket.create_connection((h,p),timeout=30) as s:
                s.settimeout(120); s.sendall(b'TTX1'+struct.pack('<BH',2,len(dest))+dest+struct.pack('<Q',size)); check(s); start=time.monotonic(); last=0
                events.put(('state',i,'Sending'))
                with f.open('rb') as stream:
                    while chunk:=stream.read(2*1024*1024):
                        if stop.is_set(): raise InterruptedError('Cancelled')
                        s.sendall(chunk); crc=zlib.crc32(chunk,crc); sent+=len(chunk); now=time.monotonic(); speed=sent/max(now-start,.001)
                        if now-last>=.2 or sent==size:
                            events.put(('progress',sent/max(size,1)*100,f'{f.name} | {speed/2**20:.2f} MiB/s | ETA {int((size-sent)/max(speed,1))//60}m {int((size-sent)/max(speed,1))%60}s')); last=now
                check(s); remote=struct.unpack('<I',recv(s,4))[0]
                if remote!=crc: raise RuntimeError('CRC32 mismatch')
                events.put(('state',i,'CRC32 passed'))
        events.put(('done','Cancelled' if stop.is_set() else 'Queue complete'))
    except Exception as e:
        events.put(('state',i,'Failed / cancelled')); events.put(('done',str(e)))

def start():
    global active
    if not host.get().strip(): return messagebox.showerror('Sender','Enter the console IP address first.')
    if not files: return messagebox.showinfo('Sender','Select a file first.')
    try:
        p=int(port.get()); assert 1<=p<=65535
    except Exception: return messagebox.showerror('Sender','Invalid port')
    items=list(files.items()); names=[pathlib.Path(n).name.casefold() for _,n in items]
    if len(names)!=len(set(names)): return messagebox.showerror('Sender','Duplicate destination filenames.')
    if not messagebox.askyesno('Confirm transfer','Send selected files? Existing destination files may be replaced.'): return
    save_host(host.get().strip())
    active=True; stop.clear(); progress['value']=0
    for b in (addbtn,removebtn,startbtn): b.state(['disabled'])
    cancelbtn.state(['!disabled']); threading.Thread(target=worker,args=(host.get().strip(),p,items),daemon=True).start()

def poll():
    global active
    while True:
        try: e=events.get_nowait()
        except queue.Empty: break
        if e[0]=='state': tree.set(e[1],'state',e[2])
        elif e[0]=='progress': progress['value']=e[1]; status.set(f'{e[1]:.2f}% | {e[2]}')
        elif e[0]=='done':
            active=False; status.set(e[1]); cancelbtn.state(['disabled'])
            for b in (addbtn,removebtn,startbtn): b.state(['!disabled'])
    root.after(100,poll)
buttons=ttk.Frame(frame); buttons.pack(fill='x'); addbtn=ttk.Button(buttons,text='Browse files',command=add); addbtn.pack(side='left'); removebtn=ttk.Button(buttons,text='Remove',command=remove); removebtn.pack(side='left',padx=8); startbtn=ttk.Button(buttons,text='Start transfer',command=start); startbtn.pack(side='right'); cancelbtn=ttk.Button(buttons,text='Cancel',command=stop.set); cancelbtn.pack(side='right',padx=8); cancelbtn.state(['disabled'])
progress=ttk.Progressbar(frame,maximum=100); progress.pack(fill='x',pady=(20,8)); status=tk.StringVar(value='Ready — open the console receiver first'); ttk.Label(frame,textvariable=status,wraplength=690).pack(anchor='w'); ttk.Label(frame,text='Unofficial client • Toronja protocol • CRC32 verification').pack(anchor='w',pady=12)
def close():
    if active: messagebox.showinfo('Sender','Cancel the transfer and wait for it to stop before closing.'); return
    root.destroy()
root.protocol('WM_DELETE_WINDOW',close); root.after(100,poll); root.mainloop()
