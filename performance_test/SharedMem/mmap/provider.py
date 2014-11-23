import mmap
import time
def showinfo(obj, doprintobj):
    t = type(obj)
    print(t)
    if(doprintobj):
        print(obj)

# write a simple example file
with open("hello.txt", "wb") as f:
    f.write(b"00Hello Python!\n")

with open("hello.txt", "r+b") as f:
    # memory-map the file, size 0 means whole file
    mm = mmap.mmap(f.fileno(), 0)
    # read content via standard file methods
    #print(mm.readline())  # prints b"Hello Python!\n"
    # read content via slice notation
    showinfo(mm, False)
    showinfo(mm[1],True)
    mm[0] = 1
    mm[1]= 1
    showinfo(mm[1],True)
    
    while(True):
        time.sleep(0.0001)        
        if(mm[0] == 2):
            mm[0] = 1
            if( mm[1] <254):
                mm[1] +=1 
            else:
                print(mm[1])
                break
        else:
            v = str(mm[0])
            pass
               
                
            
    
    # close the map
    time.sleep(2)
    mm.close()
input("done...")
