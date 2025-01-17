from flask import Flask, render_template, request, redirect, url_for
import time
import csv
from threading import Thread
from queue import Queue

app = Flask(__name__)

data_barang_sementara = []
keranjang_barang = []
def sort_data_by_nama_barang(data):
    return sorted(data, key=lambda x: x['nama_barang'])




def proses():
    for index in range(10):
        print(index)
        time.sleep(0.5)


def read_data():
    csv_data = []
    with open("mentahan.csv", "r") as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        for line in csv_reader:
            if len(line) == 4:
                row = {
                    "id": line[0],
                    "nama_barang": line[1],
                    "stok_barang": line[2],
                    "harga_barang": line[3],
                }
                csv_data.append(row)
    # Urutkan berdasarkan ID
    csv_data.sort(key=lambda x: x['id'])
    return csv_data

def convert_to_numeric(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value

def quicksort(arr, key):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    pivot_value = convert_to_numeric(pivot[key])
    left = [x for x in arr if convert_to_numeric(x[key]) < pivot_value]
    middle = [x for x in arr if convert_to_numeric(x[key]) == pivot_value]
    right = [x for x in arr if convert_to_numeric(x[key]) > pivot_value]
    return quicksort(left, key) + middle + quicksort(right, key)

def search_data(data_barang, kata_kunci, result_queue):
    for brg in data_barang:
        if brg.get("nama_barang").lower().find(kata_kunci.lower()) != -1:
            result_queue.put(brg)

        if str(brg.get('id')).lower().find(kata_kunci.lower()) != -1:
            result_queue.put(brg)



def binary_search(data, target_id):
    low, high = 0, len(data) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_id = data[mid]['id']
        if mid_id == target_id:
            return data[mid]
        elif mid_id < target_id:
            low = mid + 1
        else:
            high = mid - 1

    return None


def tambah_barang_sementara(data_barang):
    with open("mentahan.csv", "a+", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([data_barang['id'], data_barang['nama_barang'], data_barang['stok_barang'], data_barang['harga_barang']])

@app.route('/tambah_barang', methods=['POST'])
def tambah_barang():
    if request.method == 'POST':
        id_barang = request.form.get('id_barang')
        nama_barang = request.form.get('name')
        stok_barang = request.form.get('stok_barang')
        harga_barang = request.form.get('harga_barang')

        if id_barang and nama_barang and stok_barang and harga_barang:
            barang_baru = {
                'id': id_barang,
                'nama_barang': nama_barang,
                'stok_barang': stok_barang,
                'harga_barang': harga_barang
            }

            tambah_barang_sementara(barang_baru)

            return redirect(url_for('project'))
        else:
            return "Gagal menambahkan barang. Mohon lengkapi semua data."

@app.route('/tambah_ke_keranjang/<id_barang>', methods=['GET'])
def tambah_keranjang(id_barang):
    # Waktu mulai
    start_time = time.time()
    
    data = read_data()

    # Bubble sort
    result = binary_search(data, id_barang)

    end_time = time.time()  # Waktu selesai pencarian
    execution_time = end_time - start_time

    context_data = {
        "data_barang": result,
        "execution_time": float(execution_time),
    }
    return render_template('keranjang.html', **context_data)

        
@app.route('/')
def index():
    show_image = request.args.get('show_image', 'True').lower() == 'true'

    start_time = time.time()
    
    data = read_data()

    if show_image:
        return render_template('loginv2.html')
    else:
        # Tambahkan data_barang_sementara ke data menggunakan append
        data += data_barang_sementara

        # Sort the combined data by 'nama_barang'
        sorted_data = sorted(data, key=lambda x: x['nama_barang'])

        end_time = time.time() 
        execution_time= end_time - start_time
        context_data = {
            "data_barang": sorted_data,
            'execution_time' : execution_time
        }
        return render_template('intro.html', **context_data)
        
        
@app.route("/search")
def menampilkan_pencarian():
    start_time = time.time()
    kata_kunci = request.args.get('kata-kunci', '')
    kata_kunci = kata_kunci.lower()
    data_barang = read_data()
    result = binary_search(data_barang, kata_kunci)
    result = [
        brg for brg in data_barang
        if any(
            str(brg.get(key, "")).lower().find(kata_kunci) != -1
            for key in ["nama_barang", "id", "stok_barang", "harga_barang"]
        )
    ]



    end_time = time.time()  # Waktu selesai pencarian
    execution_time = end_time - start_time

    context_data = {
        "data_barang": result,
        "execution_time": execution_time
    }

    return render_template('index.html', **context_data)

@app.route('/projek')
def project():
    start_time = time.time()
    kata_kunci = request.args.get('projek', '')  # Menangkap nilai 'projek' dari parameter URL
    data_barang = read_data()

    result_queue = Queue()
    
    # Membuat thread untuk melakukan pencarian
    search_thread = Thread(target=search_data, args=(data_barang, kata_kunci, result_queue))
    search_thread.start()
    search_thread.join()  # Menunggu hingga pencarian selesai
    
    hasil_pencarian = list(result_queue.queue)

    end_time = time.time()  # Waktu selesai pencarian
    execution_time = end_time - start_time

    context_data = {
        "data_barang": hasil_pencarian,
        'execution_time': execution_time
    }
    
    return render_template('index.html', **context_data)


@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/brg')
def brg():
    return render_template('tambahbarang.html')

@app.route('/Buy')
def buy():
    return render_template('payment.html')

@app.route('/kembali')
def back():
    return render_template('index.html')

@app.route('/login')
def lgn():
    return render_template('login.html')


#pengurutan
@app.route('/sorted_barang')
def sorted_barang():
    start_time = time.time()
    data = read_data()

    # Specify the key for sorting (e.g., 'nama_barang')
    sorting_key = 'nama_barang'

    # Sort the data by the specified key using quicksort
    sorted_data = quicksort(data, sorting_key)
    end_time = time.time()
    execution_time = end_time - start_time
    context_data = {
        "data_barang": sorted_data,
        "execution_time": execution_time
    }

    return render_template('index.html', **context_data)


@app.route('/detail/<id_barang>')
def detail(id_barang):
    # Waktu mulai
    start_time = time.time()
    
    data = read_data()

    # Binary search
    result = binary_search(data, id_barang)

    end_time = time.time()  # Waktu selesai pencarian
    execution_time = end_time - start_time

    context_data = {
        "data_barang": result,
        "execution_time": float(execution_time),
    }
    return render_template('detail.html', **context_data)
if __name__ == '__main__':
    app.run(debug=True)
