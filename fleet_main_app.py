from backend.services.Service_Google_Drive import search_files

print("🔍 Listando TODOS os arquivos que a conta de serviço pode acessar...")
arquivos = search_files("trashed=false")

if arquivos:
    print("✅ Arquivos encontrados:")
    for arquivo in arquivos:
        print(f"📄 Nome: {arquivo['name']} - ID: {arquivo['id']}")
else:
    print("❌ Nenhum arquivo encontrado!")
