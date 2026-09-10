using Microsoft.Agents.AI.DurableTask.Workflows;
using Microsoft.DurableTask.Client;
using Microsoft.DurableTask.Worker;

var assemblies = new[]
{
    typeof(DurableWorkflowOptions).Assembly,
    typeof(DurableTaskClient).Assembly,
    typeof(DurableTaskWorkerOptions).Assembly,
};

foreach (var assembly in assemblies.DistinctBy(value => value.GetName().Name))
{
    Console.WriteLine($"{assembly.GetName().Name}={assembly.GetName().Version}");
}
