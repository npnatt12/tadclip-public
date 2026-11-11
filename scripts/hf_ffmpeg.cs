// hf_ffmpeg.sh for Windows. HyperFrames runs its ffmpeg as a program (HYPERFRAMES_FFMPEG_PATH), and Windows can't run a
// .sh as one, so setup.sh compiles this into scripts/hf_ffmpeg.exe with the C# compiler every Windows 10/11 has
// (PowerShell Add-Type, .NET Framework 4: C# 5 syntax only). Same two fixes as the .sh:
//   -threads from scripts/X264_THREADS right after every libx264 (same bytes on every machine; why: x264.py)
//   HyperFrames' audio mix (-/filter_complex or -filter_complex_script) goes through hf_mix_order.py first (fixed
//   input order; why: hf_mix_order.py)
// stdin/stdout/stderr pass straight through (HyperFrames pipes frames in); the exit code is ffmpeg's.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;

static class HfFfmpeg {
  // one argument quoted the way CommandLineToArgvW / the C runtime splits it back
  static string Quote(string a) {
    if (a.Length > 0 && a.IndexOfAny(new[] { ' ', '\t', '\n', '\v', '"' }) < 0) return a;
    var sb = new StringBuilder("\"");
    for (int i = 0; ; i++) {
      int bs = 0;
      while (i < a.Length && a[i] == '\\') { i++; bs++; }
      if (i == a.Length) { sb.Append('\\', bs * 2); break; }
      if (a[i] == '"') sb.Append('\\', bs * 2 + 1).Append('"');
      else sb.Append('\\', bs).Append(a[i]);
    }
    return sb.Append('"').ToString();
  }

  static string OnPath(string exe, string skip) {
    foreach (var d in (Environment.GetEnvironmentVariable("PATH") ?? "").Split(';')) {
      if (d.Trim().Length == 0) continue;
      string p;
      try { p = Path.GetFullPath(Path.Combine(d.Trim().Trim('"'), exe)); } catch { continue; }
      if (File.Exists(p) && !string.Equals(p, skip, StringComparison.OrdinalIgnoreCase)) return p;
    }
    return null;
  }

  static int Main(string[] argv) {
    string self = Process.GetCurrentProcess().MainModule.FileName, here = Path.GetDirectoryName(self);
    string t = "";
    try { t = File.ReadAllText(Path.Combine(here, "X264_THREADS")).Trim(); } catch { }
    var a = new List<string>(); string prev = "";
    foreach (var x in argv) {
      a.Add(x);
      if (t.Length > 0 && x == "libx264" && (prev.StartsWith("-c:v") || prev == "-vcodec" || prev.StartsWith("-codec:v") || prev == "-c" || prev == "-codec")) { a.Add("-threads"); a.Add(t); }
      prev = x;
    }
    string real = Environment.GetEnvironmentVariable("HF_REAL_FFMPEG");
    if (string.IsNullOrEmpty(real)) real = OnPath("ffmpeg.exe", self);
    if (real == null) { Console.Error.WriteLine("hf_ffmpeg.exe: ffmpeg not found on PATH (bash scripts/setup.sh)"); return 127; }
    string file = real; var args = new List<string>(a);
    if (a.Contains("-/filter_complex") || a.Contains("-filter_complex_script")) {
      string py = OnPath("python3.exe", null) ?? OnPath("python.exe", null);
      if (py != null) { file = py; args.InsertRange(0, new[] { "-I", Path.Combine(here, "hf_mix_order.py"), real }); }
    }
    var parts = new List<string>(); foreach (var x in args) parts.Add(Quote(x));
    var psi = new ProcessStartInfo(file, string.Join(" ", parts.ToArray())) { UseShellExecute = false };
    using (var p = Process.Start(psi)) { p.WaitForExit(); return p.ExitCode; }
  }
}
