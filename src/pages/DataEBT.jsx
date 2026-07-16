import { useState, useMemo } from 'react';
import { Search, Plus, Pencil, Upload, Download, ChevronDown, Database, AlertTriangle, CheckCircle } from 'lucide-react';
import PageHead from '../components/ui/PageHead';
import Panel from '../components/ui/Panel';
import Stat from '../components/ui/Stat';
import Note from '../components/ui/Note';
import Footer from '../components/layout/Footer';
import Field, { inputStyle } from '../components/ui/Field';
import DataTable, { Td } from '../components/ui/DataTable';
import { C } from '../lib/tokens';
import { fmt } from '../lib/utils';
import { SAMPLE_MONTHLY_ROWS, PLANT_META, PLANT_KEYS, CUACA_CONFIG } from '../lib/data';

const MONTHS = ['Semua Bulan','Januari','Februari','Maret','April','Mei','Juni',
                 'Juli','Agustus','September','Oktober','November','Desember'];

const MONTH_NAMES_ID = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'];

function formatTanggalDisplay(isoDate) {
  if (!isoDate) return '';
  const d = new Date(isoDate);
  if (isNaN(d)) return isoDate;
  return `${String(d.getDate()).padStart(2,'0')} ${MONTH_NAMES_ID[d.getMonth()]} ${d.getFullYear()}`;
}

function formatTanggalInput(displayDate) {
  if (!displayDate) return '';
  // try parse "01 Jan 2023" → "2023-01-01"
  const parts = displayDate.split(' ');
  if (parts.length !== 3) return '';
  const day = parts[0];
  const monthIdx = MONTH_NAMES_ID.indexOf(parts[1]);
  if (monthIdx === -1) return '';
  return `${parts[2]}-${String(monthIdx + 1).padStart(2,'0')}-${day}`;
}

function emptyForm() {
  return { jenis: '', tanggal: '', produksi: '', kapasitas: '', cuaca: '' };
}

export default function DataEBT() {
  const [rows, setRows]       = useState([...SAMPLE_MONTHLY_ROWS]);
  const [query, setQuery]     = useState('');
  const [tahunF, setTahunF]   = useState('Semua Tahun');
  const [bulanF, setBulanF]   = useState('Semua Bulan');
  const [jenisF, setJenisF]   = useState('Semua Jenis PLT');
  const [openPanel, setOpenPanel] = useState(null);

  // Tambah form state
  const [formAdd, setFormAdd]   = useState(emptyForm());
  const [addMsg, setAddMsg]     = useState(null); // { type: 'ok'|'err', text }

  // Edit/hapus state
  const [editId, setEditId]     = useState(null);
  const [formEdit, setFormEdit] = useState(emptyForm());
  const [editMsg, setEditMsg]   = useState(null);
  const [deletePending, setDeletePending] = useState(false);

  // Import state
  const [importMode, setImportMode] = useState('gabung');

  const shown = useMemo(() => {
    return rows.filter(r => {
      const matchQ = query === '' ||
        r.jenis.toLowerCase().includes(query.toLowerCase()) ||
        r.tanggal.toLowerCase().includes(query.toLowerCase());
      const matchJ = jenisF === 'Semua Jenis PLT' || r.jenis === jenisF;
      return matchQ && matchJ;
    });
  }, [rows, query, jenisF]);

  const cuacaAdd = CUACA_CONFIG[formAdd.jenis] || { label: 'Cuaca', satuan: '—', help: '' };
  const cuacaEdit = CUACA_CONFIG[formEdit.jenis] || { label: 'Cuaca', satuan: '—', help: '' };

  function handleAdd(e) {
    e.preventDefault();
    if (!formAdd.jenis || !formAdd.tanggal) {
      setAddMsg({ type: 'err', text: 'Jenis PLT dan Tanggal wajib diisi.' });
      return;
    }
    const newRow = {
      id: Math.max(0, ...rows.map(r => r.id)) + 1,
      tanggal: formatTanggalDisplay(formAdd.tanggal),
      jenis: formAdd.jenis,
      produksi: parseFloat(formAdd.produksi) || 0,
      kapasitas: parseFloat(formAdd.kapasitas) || 0,
      cuaca: parseFloat(formAdd.cuaca) || 0,
    };
    setRows(prev => [...prev, newRow]);
    setFormAdd(emptyForm());
    setAddMsg({ type: 'ok', text: `Data berhasil ditambahkan (ID ${newRow.id}).` });
    setTimeout(() => setAddMsg(null), 4000);
  }

  function selectForEdit(id) {
    const row = rows.find(r => r.id === id);
    if (!row) return;
    setEditId(id);
    setFormEdit({
      jenis: row.jenis,
      tanggal: formatTanggalInput(row.tanggal),
      produksi: String(row.produksi),
      kapasitas: String(row.kapasitas),
      cuaca: String(row.cuaca),
    });
    setDeletePending(false);
    setEditMsg(null);
  }

  function handleEdit(e) {
    e.preventDefault();
    if (!editId) return;
    setRows(prev => prev.map(r => r.id === editId ? {
      ...r,
      jenis: formEdit.jenis || r.jenis,
      tanggal: formatTanggalDisplay(formEdit.tanggal) || r.tanggal,
      produksi: parseFloat(formEdit.produksi) || 0,
      kapasitas: parseFloat(formEdit.kapasitas) || 0,
      cuaca: parseFloat(formEdit.cuaca) || 0,
    } : r));
    setEditMsg({ type: 'ok', text: `Data ID ${editId} berhasil diperbarui.` });
    setTimeout(() => setEditMsg(null), 4000);
  }

  function handleDelete() {
    setRows(prev => prev.filter(r => r.id !== editId));
    setEditId(null);
    setFormEdit(emptyForm());
    setDeletePending(false);
    setEditMsg({ type: 'ok', text: 'Data berhasil dihapus.' });
    setTimeout(() => setEditMsg(null), 4000);
  }

  function handleExportCSV() {
    const header = 'ID,Tanggal,Jenis_PLT,Produksi,Kapasitas,Cuaca';
    const body = rows.map(r =>
      `${r.id},${r.tanggal},${r.jenis},${r.produksi},${r.kapasitas},${r.cuaca}`
    ).join('\n');
    const blob = new Blob([header + '\n' + body], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'data_historis_ebt.csv'; a.click();
    URL.revokeObjectURL(url);
  }

  const recordOptions = rows.map(r =>
    `#${r.id} — ${r.tanggal} — ${r.jenis} — ${fmt(r.produksi, 3)} GWh`
  );

  return (
    <>
      <PageHead
        title="Data EBT — Pengelolaan Data Historis"
        desc="Kelola data historis produksi EBT sektor kelistrikan: tambah, ubah, hapus, impor, dan ekspor data."
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <Stat label="Jumlah data" value={fmt(rows.length, 0)} sub="baris observasi (tampil sample)" icon={Database} />
        <Stat label="Jumlah jenis PLT" value="7" sub="kategori pembangkit" />
        <Stat label="Rentang tahun" value="2023–2025" sub="3 tahun observasi" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
        {/* Table */}
        <Panel
          className="lg:col-span-8"
          title="Tabel data historis EBT"
          subtitle={`Menampilkan ${shown.length} dari ${rows.length} data`}
          noPad
        >
          <div className="p-4 grid grid-cols-2 sm:grid-cols-4 gap-3" style={{ borderBottom: `1px solid ${C.line}` }}>
            <Field label="Tahun">
              <select style={inputStyle()} value={tahunF} onChange={e => setTahunF(e.target.value)}>
                {['Semua Tahun','2023','2024','2025'].map(y => <option key={y}>{y}</option>)}
              </select>
            </Field>
            <Field label="Bulan">
              <select style={inputStyle()} value={bulanF} onChange={e => setBulanF(e.target.value)}>
                {MONTHS.map(m => <option key={m}>{m}</option>)}
              </select>
            </Field>
            <Field label="Jenis PLT">
              <select style={inputStyle()} value={jenisF} onChange={e => setJenisF(e.target.value)}>
                <option>Semua Jenis PLT</option>
                {PLANT_KEYS.map(k => <option key={k}>{k}</option>)}
              </select>
            </Field>
            <Field label="Cari">
              <div className="relative">
                <Search size={13} color={C.faint} style={{ position: 'absolute', left: 9, top: '50%', transform: 'translateY(-50%)' }} />
                <input
                  type="text"
                  placeholder="Jenis / tanggal…"
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  style={{ ...inputStyle(), paddingLeft: 28 }}
                />
              </div>
            </Field>
          </div>
          <DataTable
            minWidth={560}
            cols={[
              { label: 'ID', width: '8%' },
              { label: 'Tanggal', width: '22%' },
              { label: 'Jenis PLT', width: '24%' },
              { label: 'Produksi (GWh)', width: '16%', align: 'right' },
              { label: 'Kapasitas (MW)', width: '16%', align: 'right' },
              { label: 'Cuaca', width: '14%', align: 'right' },
            ]}
            rows={shown.map((r) => (
              <tr key={r.id} style={{ borderBottom: `1px solid ${C.line}` }}>
                <Td mono color={C.faint}>{r.id}</Td>
                <Td>{r.tanggal}</Td>
                <Td>
                  <span className="flex items-center gap-1.5">
                    <span style={{ width: 7, height: 7, borderRadius: '50%', background: PLANT_META[r.jenis]?.color || C.faint, display: 'inline-block', flexShrink: 0 }} />
                    <span className="truncate">{r.jenis}</span>
                  </span>
                </Td>
                <Td align="right" mono>{fmt(r.produksi, 3)}</Td>
                <Td align="right" mono>{fmt(r.kapasitas, 3)}</Td>
                <Td align="right" mono>{fmt(r.cuaca, 3)}</Td>
              </tr>
            ))}
          />
        </Panel>

        {/* Kelola data accordion */}
        <Panel className="lg:col-span-4" title="Kelola data" subtitle="Pilih tindakan yang ingin dilakukan">
          <div className="space-y-2">

            {/* ── Tambah ── */}
            <AccordionItem
              id="tambah" icon={Plus} label="Tambah data baru"
              open={openPanel} setOpen={setOpenPanel}
            >
              <form onSubmit={handleAdd} className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Jenis PLT" className="col-span-2">
                    <select
                      style={inputStyle()}
                      value={formAdd.jenis}
                      onChange={e => setFormAdd(f => ({ ...f, jenis: e.target.value }))}
                    >
                      <option value="">-- Pilih Jenis PLT --</option>
                      {PLANT_KEYS.map(k => <option key={k}>{k}</option>)}
                    </select>
                  </Field>
                  <Field label="Tanggal" className="col-span-2">
                    <input
                      type="date"
                      min="2020-01-01" max="2030-12-31"
                      style={inputStyle()}
                      value={formAdd.tanggal}
                      onChange={e => setFormAdd(f => ({ ...f, tanggal: e.target.value }))}
                    />
                  </Field>
                  <Field label="Produksi (GWh)">
                    <input type="number" min="0" step="0.001" style={inputStyle()}
                      value={formAdd.produksi}
                      onChange={e => setFormAdd(f => ({ ...f, produksi: e.target.value }))} />
                  </Field>
                  <Field label="Kapasitas (MW)">
                    <input type="number" min="0" step="0.001" style={inputStyle()}
                      value={formAdd.kapasitas}
                      onChange={e => setFormAdd(f => ({ ...f, kapasitas: e.target.value }))} />
                  </Field>
                  <Field label={`${cuacaAdd.label} (${cuacaAdd.satuan})`} className="col-span-2">
                    <input type="number" min="0" step="0.001" style={inputStyle()}
                      placeholder={cuacaAdd.help}
                      value={formAdd.cuaca}
                      onChange={e => setFormAdd(f => ({ ...f, cuaca: e.target.value }))} />
                  </Field>
                </div>
                <button type="submit"
                  className="w-full py-2 rounded-lg text-sm font-medium"
                  style={{ background: C.green, color: '#fff', border: 'none', cursor: 'pointer', fontFamily: "'Inter', sans-serif" }}>
                  Tambah Data
                </button>
                {addMsg && <MsgBanner msg={addMsg} />}
              </form>
            </AccordionItem>

            {/* ── Edit / Hapus ── */}
            <AccordionItem
              id="edit" icon={Pencil} label="Edit / hapus data"
              open={openPanel} setOpen={setOpenPanel}
            >
              <div className="space-y-3">
                <Field label="Pilih data (berdasarkan ID)">
                  <select style={inputStyle()} value={editId ?? ''}
                    onChange={e => selectForEdit(Number(e.target.value))}>
                    <option value="">-- Pilih data --</option>
                    {rows.map((r, i) => (
                      <option key={r.id} value={r.id}>{recordOptions[i]}</option>
                    ))}
                  </select>
                </Field>

                {editId !== null && (
                  <form onSubmit={handleEdit} className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <Field label="Jenis PLT" className="col-span-2">
                        <select style={inputStyle()} value={formEdit.jenis}
                          onChange={e => setFormEdit(f => ({ ...f, jenis: e.target.value }))}>
                          {PLANT_KEYS.map(k => <option key={k}>{k}</option>)}
                        </select>
                      </Field>
                      <Field label="Tanggal" className="col-span-2">
                        <input type="date" min="2020-01-01" max="2030-12-31"
                          style={inputStyle()} value={formEdit.tanggal}
                          onChange={e => setFormEdit(f => ({ ...f, tanggal: e.target.value }))} />
                      </Field>
                      <Field label="Produksi (GWh)">
                        <input type="number" min="0" step="0.001" style={inputStyle()}
                          value={formEdit.produksi}
                          onChange={e => setFormEdit(f => ({ ...f, produksi: e.target.value }))} />
                      </Field>
                      <Field label="Kapasitas (MW)">
                        <input type="number" min="0" step="0.001" style={inputStyle()}
                          value={formEdit.kapasitas}
                          onChange={e => setFormEdit(f => ({ ...f, kapasitas: e.target.value }))} />
                      </Field>
                      <Field label={`${cuacaEdit.label} (${cuacaEdit.satuan})`} className="col-span-2">
                        <input type="number" min="0" step="0.001" style={inputStyle()}
                          value={formEdit.cuaca}
                          onChange={e => setFormEdit(f => ({ ...f, cuaca: e.target.value }))} />
                      </Field>
                    </div>
                    <button type="submit"
                      className="w-full py-2 rounded-lg text-sm font-medium"
                      style={{ background: C.green, color: '#fff', border: 'none', cursor: 'pointer', fontFamily: "'Inter', sans-serif" }}>
                      Simpan Perubahan
                    </button>
                    {!deletePending ? (
                      <button type="button"
                        className="w-full py-2 rounded-lg text-sm font-medium"
                        style={{ background: '#FEE2E2', color: C.red, border: 'none', cursor: 'pointer', fontFamily: "'Inter', sans-serif" }}
                        onClick={() => setDeletePending(true)}>
                        🗑️ Hapus Data Ini
                      </button>
                    ) : (
                      <div className="rounded-lg p-3 space-y-2" style={{ background: '#FFF7ED', border: `1px solid ${C.gold}` }}>
                        <p className="text-xs font-medium" style={{ color: C.warn }}>
                          ⚠️ Yakin ingin menghapus data ID {editId}? Tindakan ini tidak dapat dibatalkan.
                        </p>
                        <div className="flex gap-2">
                          <button type="button"
                            className="flex-1 py-1.5 rounded-lg text-xs font-medium"
                            style={{ background: C.red, color: '#fff', border: 'none', cursor: 'pointer' }}
                            onClick={handleDelete}>
                            ✅ Ya, Hapus Data
                          </button>
                          <button type="button"
                            className="flex-1 py-1.5 rounded-lg text-xs font-medium"
                            style={{ background: C.line, color: C.muted, border: 'none', cursor: 'pointer' }}
                            onClick={() => setDeletePending(false)}>
                            ↩️ Batal
                          </button>
                        </div>
                      </div>
                    )}
                    {editMsg && <MsgBanner msg={editMsg} />}
                  </form>
                )}
              </div>
            </AccordionItem>

            {/* ── Impor ── */}
            <AccordionItem
              id="impor" icon={Upload} label="Impor dataset CSV/Excel"
              open={openPanel} setOpen={setOpenPanel}
            >
              <div className="space-y-3">
                <Note tone="warn">
                  Fitur impor memerlukan koneksi ke backend. Saat ini halaman berjalan <strong>offline</strong> — perubahan hanya tersimpan di sesi browser.
                </Note>
                <Field label="Mode impor">
                  <div className="flex gap-3">
                    {[['gabung','Gabungkan dengan data ada'],['ganti','Ganti seluruh dataset']].map(([v, l]) => (
                      <label key={v} className="flex items-center gap-1.5 text-xs cursor-pointer" style={{ color: C.ink }}>
                        <input type="radio" name="importMode" value={v} checked={importMode === v}
                          onChange={() => setImportMode(v)} style={{ accentColor: C.green }} />
                        {l}
                      </label>
                    ))}
                  </div>
                </Field>
                <div className="rounded-lg border-2 border-dashed p-4 text-center" style={{ borderColor: C.line }}>
                  <Upload size={20} color={C.faint} className="mx-auto mb-2" />
                  <p className="text-xs" style={{ color: C.muted }}>Seret file CSV/Excel ke sini, atau klik untuk memilih</p>
                  <p className="text-xs mt-1" style={{ color: C.faint }}>Kolom yang dibutuhkan: <code>Tanggal, Jenis_PLT, Produksi, Kapasitas, Cuaca</code></p>
                </div>
              </div>
            </AccordionItem>

            {/* ── Ekspor ── */}
            <AccordionItem
              id="ekspor" icon={Download} label="Ekspor dataset"
              open={openPanel} setOpen={setOpenPanel}
            >
              <div className="space-y-3">
                <p className="text-xs" style={{ color: C.muted }}>
                  Unduh data yang ditampilkan di tabel sebagai file CSV.
                </p>
                <button
                  onClick={handleExportCSV}
                  className="w-full flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium"
                  style={{ background: C.greenSoft, color: C.green, border: 'none', cursor: 'pointer', fontFamily: "'Inter', sans-serif" }}>
                  <Download size={14} /> Unduh CSV
                </button>
                <Note tone="info">
                  Untuk mengunduh dataset lengkap 252 baris, hubungkan ke backend dan gunakan endpoint <code>/api/data/export</code>.
                </Note>
              </div>
            </AccordionItem>
          </div>

          <div className="mt-4">
            <Note tone="warn">
              Perubahan data langsung tersimpan ke <strong>data_historis_ebt.csv</strong>, namun <strong>tidak memicu pelatihan ulang model</strong>. Untuk melatih ulang, ekspor dataset lalu jalankan pipeline di Google Colab.
            </Note>
          </div>
        </Panel>
      </div>

      <Footer />
    </>
  );
}

function AccordionItem({ id, icon: Icon, label, open, setOpen, children }) {
  const isOpen = open === id;
  return (
    <div className="rounded-lg border overflow-hidden" style={{ borderColor: C.line }}>
      <button
        className="w-full flex items-center justify-between px-3 py-2.5 text-sm font-medium border-0 bg-transparent cursor-pointer"
        style={{
          color: C.ink,
          background: isOpen ? C.greenSoft : '#fff',
          fontFamily: "'Inter', sans-serif",
        }}
        onClick={() => setOpen(isOpen ? null : id)}
      >
        <span className="flex items-center gap-2">
          <Icon size={14} color={C.green} />
          {label}
        </span>
        <ChevronDown
          size={14} color={C.faint}
          style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}
        />
      </button>
      {isOpen && (
        <div className="px-3 py-3" style={{ borderTop: `1px solid ${C.line}` }}>
          {children}
        </div>
      )}
    </div>
  );
}

function MsgBanner({ msg }) {
  const isOk = msg.type === 'ok';
  return (
    <div className="flex items-center gap-2 rounded-lg px-3 py-2 text-xs"
      style={{ background: isOk ? '#ECFDF5' : '#FEF2F2', color: isOk ? C.ok : C.red }}>
      {isOk
        ? <CheckCircle size={13} color={C.ok} />
        : <AlertTriangle size={13} color={C.red} />}
      {msg.text}
    </div>
  );
}
