import React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import MenuIcon from '@mui/icons-material/Menu';
import Tooltip from '@mui/material/Tooltip';
import { useAuth } from '../auth';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import DownloadIcon from '@mui/icons-material/Download';
import { Menu, MenuItem, ListItemIcon, ListItemText, Button, Avatar } from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import SettingsIcon from '@mui/icons-material/Settings';
import BackupIcon from '@mui/icons-material/Backup';

export default function ButtonAppBar(props) {
  const { isLoggedIn, logout } = useAuth();
  // 修改为使用用户菜单而不是单独的导入导出菜单
  const [userMenuAnchor, setUserMenuAnchor] = React.useState(null);

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleExport = () => {
    setUserMenuAnchor(null);
    exportData();
  };

  const handleImport = () => {
    setUserMenuAnchor(null);
    document.getElementById('import-file-input').click();
  };

  const handleLogout = () => {
    setUserMenuAnchor(null);
    logout();
    if (props.setIsLoggedIn) {
      props.setIsLoggedIn(false);
    }
  };

  const handleProfile = () => {
    setUserMenuAnchor(null);
    // 个人资料页面导航代码
    // 可以根据实际情况添加
  };

  const exportData = () => {
    fetch('/api/export', {
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token'),
      },
    })
    .then(response => {
      if (response.ok) {
        return response.blob();
      }
      throw new Error('Network response was not ok.');
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      a.download = `linkmanager_backup_${timestamp}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      props.setAlertInfo({
        open: true,
        message: '数据导出成功！',
        severity: 'success',
      });
    })
    .catch(error => {
      console.error('导出数据时出错:', error);
      props.setAlertInfo({
        open: true,
        message: '导出数据失败，请稍后重试。',
        severity: 'error',
      });
    });
  };

  const importData = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
      props.setAlertInfo({
        open: true,
        message: '请选择JSON格式的备份文件',
        severity: 'error',
      });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/api/import', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('token'),
      },
      body: formData,
    })
    .then(response => response.json())
    .then(data => {
      if (data.msg === "Data imported successfully") {
        props.setAlertInfo({
          open: true,
          message: '数据导入成功！页面将在3秒后刷新...',
          severity: 'success',
        });
        // 刷新页面以显示导入的数据
        setTimeout(() => {
          window.location.reload();
        }, 3000);
      } else {
        throw new Error(data.msg || '导入失败');
      }
    })
    .catch(error => {
      console.error('导入数据时出错:', error);
      props.setAlertInfo({
        open: true,
        message: `导入数据失败: ${error.message}`,
        severity: 'error',
      });
    });

    // 重置input，以便可以选择相同的文件
    event.target.value = '';
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Link Manager
          </Typography>
          
          {isLoggedIn && (
            <>
              {/* 更改为使用头像/用户图标作为下拉菜单触发器 */}
              <Tooltip title="用户选项">
                <IconButton 
                  color="inherit" 
                  onClick={handleUserMenuOpen}
                  sx={{ ml: 2 }}
                >
                  <AccountCircleIcon />
                </IconButton>
              </Tooltip>
              <Menu
                anchorEl={userMenuAnchor}
                open={Boolean(userMenuAnchor)}
                onClose={handleUserMenuClose}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
              >
                <MenuItem onClick={handleProfile}>
                  <ListItemIcon>
                    <AccountCircleIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText>个人资料</ListItemText>
                </MenuItem>
                
                {/* 数据备份选项放在个人资料下方 */}
                <MenuItem onClick={handleExport}>
                  <ListItemIcon>
                    <FileDownloadIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText>导出数据</ListItemText>
                </MenuItem>
                <MenuItem onClick={handleImport}>
                  <ListItemIcon>
                    <FileUploadIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText>导入数据</ListItemText>
                </MenuItem>
                
                <MenuItem onClick={handleLogout}>
                  <ListItemIcon>
                    <LogoutIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText>退出登录</ListItemText>
                </MenuItem>
              </Menu>
              <input
                id="import-file-input"
                type="file"
                accept=".json"
                style={{ display: 'none' }}
                onChange={importData}
              />
            </>
          )}
        </Toolbar>
      </AppBar>
    </Box>
  );
}
