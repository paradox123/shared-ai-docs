FROM mcr.microsoft.com/dotnet/sdk:10.0.203@sha256:8a90a473da5205a16979de99d2fc20975e922c68304f5c79d564e666dc3982fc AS build
WORKDIR /source
COPY global.json ./
COPY src/Directory.Build.props src/Directory.Packages.props ./src/
COPY src/Wpcp.Domain/ ./src/Wpcp.Domain/
COPY src/Wpcp.Storage.Postgres/ ./src/Wpcp.Storage.Postgres/
COPY src/Wpcp.Api/ ./src/Wpcp.Api/
RUN dotnet restore src/Wpcp.Api/Wpcp.Api.csproj --locked-mode \
    && dotnet publish src/Wpcp.Api/Wpcp.Api.csproj --no-restore -c Release -o /app

FROM mcr.microsoft.com/dotnet/aspnet:10.0@sha256:6a94333d37514e385650a3c81a55e5350b67253dbe136e9cf17e499c35606a8c
WORKDIR /app
COPY --from=build /app/ ./
USER app
ENTRYPOINT ["dotnet", "Wpcp.Api.dll"]
CMD ["--submission-config", "/config/submission.json", "--urls", "http://127.0.0.1:5080"]
