// ConvertToPdf.cs — .NET 10 file-based app (no .csproj)
// Compiles a Typst file to PDF using the `typst` CLI.
//
// Usage:
//   dotnet run /path/to/ConvertToPdf.cs -- <input.typ> <output.pdf>

using System.Diagnostics;

if (args.Length < 2)
{
    Console.Error.WriteLine("Usage: ConvertToPdf.cs <input.typ> <output.pdf>");
    return 1;
}

var inputTyp = args[0];
var outputPdf = args[1];

if (!File.Exists(inputTyp))
{
    Console.Error.WriteLine($"Error: input file not found: {inputTyp}");
    return 1;
}

var psi = new ProcessStartInfo
{
    FileName = "typst",
    Arguments = $"compile \"{inputTyp}\" \"{outputPdf}\"",
    RedirectStandardOutput = true,
    RedirectStandardError = true,
    UseShellExecute = false,
};

Console.WriteLine($"Compiling: {Path.GetFileName(inputTyp)} → {Path.GetFileName(outputPdf)}");

var process = Process.Start(psi);
if (process is null)
{
    Console.Error.WriteLine("Error: failed to start typst process. Is typst installed? (brew install typst)");
    return 1;
}

var stderr = process.StandardError.ReadToEnd();
process.WaitForExit();

if (process.ExitCode != 0)
{
    Console.Error.WriteLine($"typst error:\n{stderr}");
    return 1;
}

Console.WriteLine($"✅ PDF created: {outputPdf}");
return 0;
