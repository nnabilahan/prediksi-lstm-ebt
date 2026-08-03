import { useState, useMemo, useEffect, useRef } from 'react';
import { Search, Plus, Pencil, Upload, Download, ChevronDown, Database, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';
import PageHead from '../components/ui/PageHead';
import Panel from '../components/ui/Panel';
import Stat from '../components/ui/Stat';
import Note from '../components/ui/Note';
import Footer from '../components/layout/Footer';
import Field, { inputStyle } from '../components/ui/Field';
import DataTable, { Td } from '../components/ui/DataTable';
import { C } from '../lib/tokens';
import { fmt } from '../lib/utils';
import { apiGet, apiPost, apiPut, apiDelete, apiPostForm, apiDownload } from '../lib/api';
import { PLANT_META, PLANT_KEYS, CUACA_CONFIG } from '../lib/data';

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

// Bentuk baris API (GET/POST/PUT /api/data) -> bentuk baris yang dipakai
// tabel & form di halaman ini (tanggal sudah dalam format tampilan).
function apiRowToUiRow(r) {
  return {
    id: r.id,
    tanggal: formatTanggalDisplay(r.tanggal),
    jenis: r.jenis_plt,
    produksi: r.produksi,
    kapasitas: r.kapasitas,
    cuaca: r.cuaca,
    sumber: r.sumber,
  };
}

export default function DataEBT() {
  const [rows, setRows]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [query, setQuery]     = useState('');
  const [tahunF, setTahunF]   = useState('Semua Tahun');
  const [bulanF, setBulanF]   = useState('Semua Bulan');
  const [jenisF, setJenisF]   = useState('Semua Jenis PLT');
  const [openPanel, setOpenPanel] = useState(null);

  // Tambah form state
  const [formAdd, setFormAdd]   = useState(emptyForm());
  const [addMsg, setAddMsg]     = useState(null); // { type: 'ok'|'err', text }
  const [addLoading, setAddLoading] = useState(false);

  // Edit/hapus state
  const [editId, setEditId]     = useState(null);
  const [formEdit, setFormEdit] = useState(emptyForm());
  const [editMsg, setEditMsg]   = useState(null);
  const [editLoading, setEditLoading] = useState(false);
  const [deletePending, setDeletePending] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Import state
  const fileInputRef = useRef(null);
  const [importLoading, setImportLoading] = useState(false);
  const [importMsg, setImportMsg] = useState(null);

  // Ekspor state
  const [exportLoading, setExportLoading] = useState(false);
  const [exportMsg, setExportMsg] = useState(null);

  async function fetchRows() {
    setLoading(true);
    setLoadError(null);
    try {
      // limit=500 mengambil seluruh dataset dalam satu panggilan (jauh di
      // atas 252 baris awal) -- halaman ini memfilter/mencari di sisi
      // klien, jadi filter Tahun/Bulan/Jenis/Cari butuh seluruh baris,
      // bukan satu halaman pagination server.
      const data = await apiGet('/api/data?limit=500&offset=0');
      setRows(data.items.map(apiRowToUiRow));
    } catch (err) {
      setLoadError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchRows(); }, []);

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

  async function handleAdd(e) {
    e.preventDefault();
    if (!formAdd.jenis || !formAdd.tanggal) {
      setAddMsg({ type: 'err', text: 'Jenis PLT dan Tanggal wajib diisi.' });
      return;
    }
    setAddLoading(true);
    setAddMsg(null);
    try {
      const created = await apiPost('/api/data', {
        tanggal: formAdd.tanggal,
        jenis_plt: formAdd.jenis,
        produksi: parseFloat(formAdd.produksi) || 0,
        kapasitas: parseFloat(formAdd.kapasitas) || 0,
        cuaca: parseFloat(formAdd.cuaca) || 0,
      });
      setRows(prev => [...prev, apiRowToUiRow(created)]);
      setFormAdd(emptyForm());
      setAddMsg({ type: 'ok', text: `Data berhasil ditambahkan (ID ${created.id}).` });
      setTimeout(() => setAddMsg(null), 4000);
    } catch (err) {
      setAddMsg({ type: 'err', text: err.message });
    } finally {
      setAddLoading(false);
    }
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

  async function handleEdit(e) {
    e.preventDefault();
    if (!editId) return;
    setEditLoading(true);
    setEditMsg(null);
    try {
      const updated = await apiPut(`/api/data/${editId}`, {
        tanggal: formEdit.tanggal,
        jenis_plt: formEdit.jenis,
        produksi: parseFloat(formEdit.produksi) || 0,
        kapasitas: parseFloat(formEdit.kapasitas) || 0,
        cuaca: parseFloat(formEdit.cuaca) || 0,
      });
      setRows(prev => prev.map(r => r.id === editId ? apiRowToUiRow(updated) : r));
      setEditMsg({ type: 'ok', text: `Data ID ${editId} berhasil diperbarui.` });
      setTimeout(() => setEditMsg(null), 4000);
    } catch (err) {
      setEditMsg({ type: 'err', text: err.message });
    } finally {
      setEditLoading(false);
    }
  }

  async function handleDelete() {
    setDeleteLoading(true);
    try {
      await apiDelete(`/api/data/${editId}`);
      setRows(prev => prev.filter(r => r.id !== editId));
      setEditId(null);
      setFormEdit(emptyForm());
      setDeletePending(false);
      setEditMsg({ type: 'ok', text: 'Data berhasil dihapus.' });
      setTimeout(() => setEditMsg(null), 4000);
    } catch (err) {
      setEditMsg({ type: 'err', text: err.message });
    } finally {
      setDeleteLoading(false);
    }
  }

  async function handleExport() {
    setExportLoading(true);
    setExportMsg(null);
    try {
      await apiDownload('/api/data/export', 'data_historis_ebt.csv');
    } catch (err) {
      setExportMsg({ type: 'err', text: err.message });
    } finally {
      setExportLoading(false);
    }
  }

  async function handleImportFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImportLoading(true);
    setImportMsg(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const result = await apiPostForm('/api/data/import', formData);
      setImportMsg({ type: 'ok', text: result.pesan });
      await fetchRows();
    } catch (err) {
      setImportMsg({ type: 'err', text: err.message });
    } finally {
      setImportLoading(false);
      e.target.value = '';
    }
  }

  const recordOptions = rows.map(r =>
    `#${r.id} — ${r.tanggal} — ${r.jenis} — ${fmt(r.produksi, 3)} GWh`
  );

  const tahunList = rows.map(r => parseInt(r.tanggal.slice(-4), 10)).filter(y => !isNaN(y));
  const rentangTahun = tahunList.length > 0
    ? (Math.min(...tahunList) === Math.max(...tahunList)
        ? String(Math.min(...tahunList))
        : `${Math.min(...tahunList)}–${Math.max(...tahunList)}`)
    : '—';

  return (
    <>
      <PageHead
        title="Data EBT — Pengelolaan Data Historis"
        desc="Kelola data historis produksi EBT sektor kelistrikan: tambah, ubah, hapus, impor, dan ekspor data."
      />

      {loadError && (
        <Note tone="warn">
          <strong>Tidak dapat memuat data dari backend:</strong> {loadError}{' '}
          <button
            onClick={fetchRows}
            className="underline font-medium"
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', padding: 0 }}
          >
            Coba lagi
          </button>
        </Note>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <Stat label="Jumlah data" value={fmt(rows.length, 0)} sub="baris observasi" icon={Database} />
        <Stat label="Jumlah jenis PLT" value="7" sub="kategori pembangkit" />
        <Stat label="Rentang tahun" value={rentangTahun} sub={`${tahunList.length} baris observasi`} />
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
          {loading ? (
            <div className="flex items-center justify-center gap-2 py-12 text-sm" style={{ color: C.muted }}>
              <Loader2 size={16} className="animate-spin" />
              Memuat data dari backend…
            </div>
          ) : (
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
          )}
          <div className="p-4" style={{ borderTop: `1px solid ${C.line}` }}>
            <Note tone="warn">
              <strong>Kolom Produksi adalah hasil disagregasi bulanan dari angka tahunan Dinas ESDM Sulsel</strong> — angka tahunan tersebut merupakan kalkulasi (Kapasitas × Capacity Factor asumsi × 8760 jam), bukan metering langsung. Kolom Cuaca adalah data riil NASA POWER.
            </Note>
          </div>
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
                <button type="submit" disabled={addLoading}
                  className="w-full flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium"
                  style={{ background: C.green, color: '#fff', border: 'none', cursor: addLoading ? 'default' : 'pointer', opacity: addLoading ? 0.7 : 1, fontFamily: "'Inter', sans-serif" }}>
                  {addLoading && <Loader2 size={14} className="animate-spin" />}
                  {addLoading ? 'Menyimpan…' : 'Tambah Data'}
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
                    <button type="submit" disabled={editLoading}
                      className="w-full flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium"
                      style={{ background: C.green, color: '#fff', border: 'none', cursor: editLoading ? 'default' : 'pointer', opacity: editLoading ? 0.7 : 1, fontFamily: "'Inter', sans-serif" }}>
                      {editLoading && <Loader2 size={14} className="animate-spin" />}
                      {editLoading ? 'Menyimpan…' : 'Simpan Perubahan'}
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
                          <button type="button" disabled={deleteLoading}
                            className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-medium"
                            style={{ background: C.red, color: '#fff', border: 'none', cursor: deleteLoading ? 'default' : 'pointer', opacity: deleteLoading ? 0.7 : 1 }}
                            onClick={handleDelete}>
                            {deleteLoading && <Loader2 size={12} className="animate-spin" />}
                            {deleteLoading ? 'Menghapus…' : '✅ Ya, Hapus Data'}
                          </button>
                          <button type="button" disabled={deleteLoading}
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
                <Note tone="info">
                  File yang diunggah akan <strong>ditambahkan</strong> ke data yang sudah ada (bukan menggantikan). Baris tersimpan dengan sumber = <code>input_pengguna</code>.
                </Note>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleImportFile}
                  className="hidden"
                  disabled={importLoading}
                />
                <div
                  onClick={() => !importLoading && fileInputRef.current?.click()}
                  className="rounded-lg border-2 border-dashed p-4 text-center"
                  style={{ borderColor: C.line, cursor: importLoading ? 'default' : 'pointer', opacity: importLoading ? 0.6 : 1 }}
                >
                  {importLoading ? (
                    <>
                      <Loader2 size={20} color={C.faint} className="mx-auto mb-2 animate-spin" />
                      <p className="text-xs" style={{ color: C.muted }}>Mengunggah &amp; memvalidasi file…</p>
                    </>
                  ) : (
                    <>
                      <Upload size={20} color={C.faint} className="mx-auto mb-2" />
                      <p className="text-xs" style={{ color: C.muted }}>Klik untuk memilih file CSV/Excel</p>
                      <p className="text-xs mt-1" style={{ color: C.faint }}>Kolom yang dibutuhkan: <code>Tanggal, Jenis_PLT (atau Jenis), Produksi, Kapasitas, Cuaca</code></p>
                    </>
                  )}
                </div>
                {importMsg && <MsgBanner msg={importMsg} />}
              </div>
            </AccordionItem>

            {/* ── Ekspor ── */}
            <AccordionItem
              id="ekspor" icon={Download} label="Ekspor dataset"
              open={openPanel} setOpen={setOpenPanel}
            >
              <div className="space-y-3">
                <p className="text-xs" style={{ color: C.muted }}>
                  Unduh seluruh dataset dari backend sebagai file CSV.
                </p>
                <button
                  onClick={handleExport}
                  disabled={exportLoading}
                  className="w-full flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium"
                  style={{ background: C.greenSoft, color: C.green, border: 'none', cursor: exportLoading ? 'default' : 'pointer', opacity: exportLoading ? 0.7 : 1, fontFamily: "'Inter', sans-serif" }}>
                  {exportLoading ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
                  {exportLoading ? 'Menyiapkan file…' : 'Unduh CSV'}
                </button>
                {exportMsg && <MsgBanner msg={exportMsg} />}
              </div>
            </AccordionItem>
          </div>

          <div className="mt-4">
            <Note tone="warn">
              Perubahan data langsung tersimpan ke <strong>database backend</strong>, namun <strong>tidak memicu pelatihan ulang model</strong>. Untuk melatih ulang, ekspor dataset lalu jalankan pipeline di Google Colab.
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
