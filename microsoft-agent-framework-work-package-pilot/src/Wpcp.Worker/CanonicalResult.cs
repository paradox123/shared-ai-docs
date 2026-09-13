using System.Diagnostics;
using System.Text.Json;

namespace Wpcp.Worker;

internal static class CanonicalResult
{
    public static async Task<bool> ValidateAsync(string python, JsonElement result, CancellationToken token)
    {
        var start = new ProcessStartInfo(python) { RedirectStandardInput = true,
            RedirectStandardOutput = true, RedirectStandardError = true, UseShellExecute = false };
        start.ArgumentList.Add(Path.Combine(AppContext.BaseDirectory, "codex_contract.py"));
        using var process = Process.Start(start) ?? throw new IOException("Validator unavailable.");
        var output = process.StandardOutput.ReadToEndAsync(token);
        var errors = process.StandardError.ReadToEndAsync(token);
        await process.StandardInput.WriteAsync(result.GetRawText());
        process.StandardInput.Close();
        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(token);
        timeout.CancelAfter(TimeSpan.FromSeconds(5));
        try { await process.WaitForExitAsync(timeout.Token); }
        catch (OperationCanceledException)
        {
            process.Kill(entireProcessTree: true);
            await process.WaitForExitAsync(CancellationToken.None);
            throw;
        }
        await Task.WhenAll(output, errors);
        return process.ExitCode == 0 && (await output).Trim() == "valid";
    }
}
