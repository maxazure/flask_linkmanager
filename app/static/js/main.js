// 文档加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // API密钥复制功能
    const copyButtons = document.querySelectorAll('.copy-api-key');
    if (copyButtons.length > 0) {
        copyButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                const keyValue = this.getAttribute('data-key');
                navigator.clipboard.writeText(keyValue).then(function() {
                    // 复制成功，更改按钮文本
                    button.innerHTML = '<i class="fas fa-check"></i> 已复制';
                    setTimeout(function() {
                        button.innerHTML = '<i class="fas fa-copy"></i> 复制';
                    }, 2000);
                }, function() {
                    // 复制失败
                    alert('复制失败，请手动复制');
                });
            });
        });
    }

    // 确认删除操作
    const deleteButtons = document.querySelectorAll('.confirm-delete');
    if (deleteButtons.length > 0) {
        deleteButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                if (!confirm('确定要删除吗？此操作不可撤销！')) {
                    e.preventDefault();
                }
            });
        });
    }

    // 自动隐藏提示框
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(function() {
            alerts.forEach(function(alert) {
                $(alert).alert('close');
            });
        }, 5000);
    }

    // 为Select2初始化标签选择器（如果存在）
    if (typeof $.fn.select2 !== 'undefined' && document.querySelector('#tags')) {
        $('#tags').select2({
            placeholder: '选择标签',
            allowClear: true,
            width: '100%'
        });
    }
});
