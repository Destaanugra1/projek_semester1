def tambah_barang_sementara(data_barang):
    with open("mentahan.csv", "a+") as file:
        file.write(f"\n{data_barang['id']},{data_barang['nama_barang']},{data_barang['stok_barang']},{data_barang['harga_barang']}\n")
