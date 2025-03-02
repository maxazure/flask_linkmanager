// ...existing code...

export default function LinkList() {
  // ...existing code...
  
  const fetchData = useCallback(() => {
    // ...existing fetch code...
  }, [categoryId, searchQuery, sortBy, sortOrder, page]);
  
  // 添加一个刷新函数，可以在导入数据后调用
  const refreshData = () => {
    fetchData();
  };
  
  // ...existing code...
}
