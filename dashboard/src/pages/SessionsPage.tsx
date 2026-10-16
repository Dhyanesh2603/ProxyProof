import React, { useState, useEffect } from 'react';
import { Plus, Play, Square, Radio, Download, RefreshCw, Calendar, Clock, Wifi } from 'lucide-react';
import { api } from '../services/api';
import { AttendanceSession, Course } from '../types';
import { Badge } from '../components/Badge';
import { Modal } from '../components/Modal';

interface SessionsPageProps {
  onSelectSession: (id: number) => void;
}

export const SessionsPage: React.FC<SessionsPageProps> = ({ onSelectSession }) => {
  const [sessions, setSessions] = useState<AttendanceSession[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // Form states
  const [courseId, setCourseId] = useState<number>(1);
  const [durationMinutes, setDurationMinutes] = useState<number>(60);
  const [rssiThreshold, setRssiThreshold] = useState<number>(-75);
  const [rotationInterval, setRotationInterval] = useState<number>(5);
  const [submitting, setSubmitting] = useState<boolean>(false);

  // Quick course create states
  const [newCourseCode, setNewCourseCode] = useState<string>('');
  const [newCourseName, setNewCourseName] = useState<string>('');
  const [newCourseSection, setNewCourseSection] = useState<string>('A');
  const [showAddCourse, setShowAddCourse] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sessList, courseList] = await Promise.all([
        api.getSessions(),
        api.getCourses()
      ]);
      setSessions(sessList);
      setCourses(courseList);
      if (courseList.length > 0 && !courseId) {
        setCourseId(courseList[0].id);
      }
    } catch (err) {
      console.error('Error loading sessions', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      let targetCourseId = courseId;

      if (showAddCourse) {
        const createdCourse = await api.createCourse({
          code: newCourseCode,
          name: newCourseName,
          section: newCourseSection
        });
        targetCourseId = createdCourse.id;
      }

      await api.createSession({
        course_id: targetCourseId,
        duration_minutes: durationMinutes,
        rssi_threshold: rssiThreshold,
        token_rotation_interval: rotationInterval
      });

      setIsModalOpen(false);
      setShowAddCourse(false);
      await loadData();
    } catch (err: any) {
      alert(`Error creating session: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleStartSession = async (id: number) => {
    try {
      await api.startSession(id);
      await loadData();
      onSelectSession(id);
    } catch (err: any) {
      alert(`Failed to start session: ${err.message}`);
    }
  };

  const handleEndSession = async (id: number) => {
    if (!window.confirm('Are you sure you want to end this session?')) return;
    try {
      await api.endSession(id);
      await loadData();
    } catch (err: any) {
      alert(`Failed to end session: ${err.message}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-[#27272a]">
        <div>
          <h1 className="text-lg font-bold tracking-tight text-white">Attendance Sessions</h1>
          <p className="text-xs text-zinc-400 mt-1">Manage BLE broadcasting windows, course allocations, and active sessions.</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-zinc-100 hover:bg-white text-zinc-950 text-xs font-semibold transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Session</span>
        </button>
      </div>

      {/* Table */}
      <div className="bg-[#121214] border border-[#27272a] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left enterprise-table">
            <thead>
              <tr className="bg-[#0e0e10]">
                <th className="py-2.5 px-4">Session Code</th>
                <th className="py-2.5 px-4">Course</th>
                <th className="py-2.5 px-4">Section</th>
                <th className="py-2.5 px-4">Duration</th>
                <th className="py-2.5 px-4">RSSI Threshold</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Started At</th>
                <th className="py-2.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/40">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-xs text-zinc-500">
                    <RefreshCw className="w-4 h-4 animate-spin inline mr-2" />
                    Loading sessions...
                  </td>
                </tr>
              ) : sessions.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-xs text-zinc-500">
                    No sessions created yet. Click "New Session" above to begin.
                  </td>
                </tr>
              ) : (
                sessions.map((sess) => (
                  <tr key={sess.id} className="hover:bg-zinc-900/40 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-white text-xs">
                      {sess.session_code}
                    </td>
                    <td className="py-3 px-4 text-xs font-medium text-zinc-200">
                      <div>{sess.course_code}</div>
                      <div className="text-[11px] text-zinc-500 truncate max-w-xs">{sess.course_name}</div>
                    </td>
                    <td className="py-3 px-4 text-xs text-zinc-400 font-mono">
                      {sess.section}
                    </td>
                    <td className="py-3 px-4 text-xs text-zinc-400 font-mono">
                      {sess.duration_minutes} min
                    </td>
                    <td className="py-3 px-4 text-xs text-zinc-400 font-mono">
                      {sess.rssi_threshold} dBm
                    </td>
                    <td className="py-3 px-4">
                      <Badge status={sess.status} />
                    </td>
                    <td className="py-3 px-4 text-xs text-zinc-400 font-mono">
                      {sess.started_at ? new Date(sess.started_at).toLocaleString() : '---'}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        {sess.status === 'SCHEDULED' && (
                          <button
                            onClick={() => handleStartSession(sess.id)}
                            className="p-1 rounded text-emerald-400 hover:bg-emerald-950/40 border border-emerald-900/50 text-xs flex items-center gap-1 px-2"
                            title="Start Session"
                          >
                            <Play className="w-3 h-3 fill-current" />
                            <span>Start</span>
                          </button>
                        )}

                        {sess.status === 'ACTIVE' && (
                          <>
                            <button
                              onClick={() => onSelectSession(sess.id)}
                              className="p-1 rounded text-zinc-200 hover:bg-zinc-800 border border-zinc-700 text-xs flex items-center gap-1 px-2"
                              title="Open Live Monitor"
                            >
                              <Radio className="w-3 h-3 text-emerald-400 animate-pulse" />
                              <span>Monitor</span>
                            </button>
                            <button
                              onClick={() => handleEndSession(sess.id)}
                              className="p-1 rounded text-rose-400 hover:bg-rose-950/40 border border-rose-900/50 text-xs flex items-center gap-1 px-2"
                              title="End Session"
                            >
                              <Square className="w-3 h-3 fill-current" />
                              <span>End</span>
                            </button>
                          </>
                        )}

                        <a
                          href={api.exportCsvUrl(sess.id)}
                          download
                          className="p-1.5 rounded text-zinc-400 hover:text-white hover:bg-zinc-800"
                          title="Export CSV"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </a>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Session Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create New Attendance Session"
      >
        <form onSubmit={handleCreateSession} className="space-y-4">
          {!showAddCourse ? (
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-medium text-zinc-300">Course & Section</label>
                <button
                  type="button"
                  onClick={() => setShowAddCourse(true)}
                  className="text-[11px] text-zinc-400 hover:text-white underline"
                >
                  + Add New Course
                </button>
              </div>
              <select
                value={courseId}
                onChange={(e) => setCourseId(parseInt(e.target.value, 10))}
                className="w-full bg-[#09090b] border border-[#27272a] rounded px-3 py-2 text-xs text-zinc-200 focus:outline-hidden focus:border-zinc-500 font-mono"
              >
                {courses.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.code} &mdash; {c.name} (Section {c.section})
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <div className="p-3 bg-zinc-950 border border-zinc-800 rounded space-y-2">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-white">Create New Course</span>
                <button
                  type="button"
                  onClick={() => setShowAddCourse(false)}
                  className="text-[11px] text-zinc-500 hover:text-zinc-300"
                >
                  Cancel
                </button>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] text-zinc-400 uppercase">Code</label>
                  <input
                    type="text"
                    placeholder="e.g. CS410"
                    value={newCourseCode}
                    onChange={(e) => setNewCourseCode(e.target.value)}
                    className="w-full bg-[#09090b] border border-zinc-800 rounded p-1.5 text-xs text-white"
                    required
                  />
                </div>
                <div>
                  <label className="text-[10px] text-zinc-400 uppercase">Section</label>
                  <input
                    type="text"
                    placeholder="e.g. A"
                    value={newCourseSection}
                    onChange={(e) => setNewCourseSection(e.target.value)}
                    className="w-full bg-[#09090b] border border-zinc-800 rounded p-1.5 text-xs text-white"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="text-[10px] text-zinc-400 uppercase">Course Name</label>
                <input
                  type="text"
                  placeholder="e.g. Advanced Operating Systems"
                  value={newCourseName}
                  onChange={(e) => setNewCourseName(e.target.value)}
                  className="w-full bg-[#09090b] border border-zinc-800 rounded p-1.5 text-xs text-white"
                  required
                />
              </div>
            </div>
          )}

          <div>
            <label className="text-xs font-medium text-zinc-300 block mb-1">Duration (Minutes)</label>
            <input
              type="number"
              min="5"
              max="240"
              value={durationMinutes}
              onChange={(e) => setDurationMinutes(parseInt(e.target.value, 10))}
              className="w-full bg-[#09090b] border border-[#27272a] rounded px-3 py-2 text-xs text-zinc-200 focus:outline-hidden focus:border-zinc-500 font-mono"
              required
            />
          </div>

          <div>
            <div className="flex items-center justify-between text-xs font-medium text-zinc-300 mb-1">
              <span>Proximity RSSI Cutoff Threshold</span>
              <span className="font-mono text-emerald-400">{rssiThreshold} dBm</span>
            </div>
            <input
              type="range"
              min="-90"
              max="-50"
              value={rssiThreshold}
              onChange={(e) => setRssiThreshold(parseInt(e.target.value, 10))}
              className="w-full accent-emerald-500 h-1.5 bg-zinc-800 rounded cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-zinc-500 mt-0.5">
              <span>-90 dBm (Permissive)</span>
              <span>-75 dBm (Standard Room)</span>
              <span>-50 dBm (Strict / Front Rows)</span>
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-zinc-300 block mb-1">
              BLE Token Rotation Interval (Seconds)
            </label>
            <select
              value={rotationInterval}
              onChange={(e) => setRotationInterval(parseInt(e.target.value, 10))}
              className="w-full bg-[#09090b] border border-[#27272a] rounded px-3 py-2 text-xs text-zinc-200 focus:outline-hidden focus:border-zinc-500 font-mono"
            >
              <option value="3">3 seconds (Extreme Security)</option>
              <option value="5">5 seconds (Recommended Default)</option>
              <option value="10">10 seconds (High Congestion)</option>
            </select>
          </div>

          <div className="pt-3 border-t border-[#27272a] flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-3 py-1.5 text-xs text-zinc-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-1.5 bg-zinc-100 hover:bg-white text-zinc-950 font-semibold text-xs rounded transition-colors disabled:opacity-50"
            >
              {submitting ? 'Creating...' : 'Create Session'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
