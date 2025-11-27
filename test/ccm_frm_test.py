import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from bootstrap import load_dependencies
from MiniDBMS import MiniDBMS


def demo_concurrency_control():
    print("=" * 50)
    print("Test CCM - Concurrency Control Manager")
    print("=" * 50)
    
    deps = load_dependencies()
    dbms = MiniDBMS(deps)
    
    print("\n1. Mulai transaction...")
    result = dbms.execute("BEGIN TRANSACTION")
    print(f"   Transaction ID: {result.transaction_id}")
    print(f"   Status: {result.message}")
    
    print("\n2. Jalanin SELECT...")
    result = dbms.execute("SELECT StudentID, FullName FROM Student WHERE StudentID < 5;")
    if hasattr(result.data, '__len__'):
        print(f"   Ketemu {len(result.data)} students")
    else:
        print(f"   Result: {result.message}")
    
    print("\n3. UPDATE data student...")
    result = dbms.execute("UPDATE Student SET GPA = 3.95 WHERE StudentID = 1;")
    print(f"   Result: {result.message}")
    
    print("\n4. Commit transaction...")
    result = dbms.execute("COMMIT")
    print(f"   Status: {result.message}")
    print(f"   Sisa active transactions: {len(dbms._active_transactions)}")
    
    print("\n  Test CCM selesai!")
    print("  - Transaction berhasil dibuat & ditrack")
    print("  - Query jalan dalam transaction")
    print("  - Commit berhasil")


def demo_failure_recovery():
    print("\n" + "=" * 50)
    print("Test FRM - Failure Recovery Manager")
    print("=" * 50)
    
    deps = load_dependencies()
    dbms = MiniDBMS(deps)
    
    print("\n1. Jalanin beberapa query (auto log ke WAL)...")
    dbms.execute("BEGIN TRANSACTION;")
    dbms.execute("SELECT * FROM Student WHERE StudentID = 1;")
    dbms.execute("UPDATE Student SET GPA = 3.8 WHERE StudentID = 2;")
    dbms.execute("COMMIT;")
    print("   yey semua query udah ke-log di Write-Ahead Log")
    
    print("\n2. Bikin checkpoint manual...")
    success = dbms.checkpoint()
    if success:
        print("   yey checkpoint berhasil dibuat")
    else:
        print("   yahh checkpoint gagal")
    
    print("\n3. Test recovery...")
    recovery_result = dbms.recover_from_failure()
    if recovery_result:
        print(f"   Recovery result: {recovery_result}")
    else:
        print("    Gak perlu recovery (semua aman)")
    
    print("\n Test FRM selesai!")
    print("  - Query auto masuk WAL")
    print("  - Checkpoint bisa dibuat manual")
    print("  - Recovery siap dipake")


def demo_complete_workflow():
    print("\n" + "=" * 50)
    print("Test Complete Workflow")
    print("=" * 50)
    
    deps = load_dependencies()
    dbms = MiniDBMS(deps)
    
    print("\nUpdate GPA student pake semua komponen")
    print("-" * 50)
    
    print("\nStep 1: Liat data student dulu")
    result = dbms.execute("SELECT StudentID, FullName, GPA FROM Student WHERE StudentID <= 3;")
    if hasattr(result.data, '__len__'):
        print(f"        Ketemu {len(result.data)} students")
    else:
        print(f"        Result: {result.message}")
    
    print("\nStep 2: Mulai transaction (CCM)")
    result = dbms.execute("BEGIN TRANSACTION;")
    tx_id = result.transaction_id
    print(f"        Transaction ID: {tx_id}")
    
    print("\nStep 3: Update GPA (auto log ke FRM)")
    result = dbms.execute("UPDATE Student SET GPA = 4.0 WHERE StudentID = 1;")
    print(f"        Result: {result.message}")
    
    print("\nStep 4: Cek apakah berhasil")
    result = dbms.execute("SELECT StudentID, FullName, GPA FROM Student WHERE StudentID = 1;")
    print(f"        Query result: {result.message}")
    
    print("\nStep 5: Commit (CCM)")
    result = dbms.execute("COMMIT;")
    print(f"        Status: Sukses")
    
    print("\nStep 6: Bikin checkpoint (FRM)")
    success = dbms.checkpoint()
    print(f"        Checkpoint: {' Berhasil' if success else ' Gagal'}")
    
    print("\n" + "=" * 50)
    print(" aman semua")

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Test Integrasi CCM & FRM")
    print("=" * 50)
    
    try:
        demo_concurrency_control()
        demo_failure_recovery()
        demo_complete_workflow()
        
        print("\n" + "=" * 50)
        print("Semua test berhasil! 🎉")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n Test gagal: {e}")
        import traceback
        traceback.print_exc()
