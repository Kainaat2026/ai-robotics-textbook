/**
 * Custom Navbar - Wraps Docusaurus navbar to add UserMenu
 */

import React from 'react';
import OriginalNavbar from '@theme-original/Navbar';
import UserMenu from '@site/src/components/Auth/UserMenu';
import styles from './styles.module.css';

export default function Navbar(props): JSX.Element {
  return (
    <div className={styles.navbarWrapper}>
      <OriginalNavbar {...props} />
      <div className={styles.userMenuContainer}>
        <UserMenu />
      </div>
    </div>
  );
}
